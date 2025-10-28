import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
import aiohttp

logger = logging.getLogger(__name__)


class ASRStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.dialect = self.scope['url_route']['kwargs'].get('dialect', 'sheng')
        self.asr_session = None
        
        await self.accept()
        
        logger.info(f"ASR WebSocket connected for user {self.user.username}, dialect: {self.dialect}")
    
    async def disconnect(self, close_code):
        if self.asr_session:
            await self.asr_session.close()
        
        logger.info(f"ASR WebSocket disconnected for user {self.user.username}")
    
    async def receive(self, text_data=None, bytes_data=None):
        try:
            if text_data:
                data = json.loads(text_data)
                action = data.get('action')
                
                if action == 'start':
                    await self.start_streaming()
                elif action == 'stop':
                    await self.stop_streaming()
                elif action == 'config':
                    self.dialect = data.get('dialect', self.dialect)
                    await self.send(text_data=json.dumps({
                        'type': 'config_updated',
                        'dialect': self.dialect
                    }))
            
            elif bytes_data:
                await self.process_audio_chunk(bytes_data)
        
        except Exception as e:
            logger.error(f"Error in ASR WebSocket receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def start_streaming(self):
        await self.send(text_data=json.dumps({
            'type': 'streaming_started',
            'dialect': self.dialect
        }))
        
        logger.info(f"ASR streaming started for user {self.user.username}")
    
    async def stop_streaming(self):
        if self.asr_session:
            await self.asr_session.close()
            self.asr_session = None
        
        await self.send(text_data=json.dumps({
            'type': 'streaming_stopped'
        }))
        
        logger.info(f"ASR streaming stopped for user {self.user.username}")
    
    async def process_audio_chunk(self, audio_data):
        try:
            asr_url = f"{settings.ASR_SERVICE_URL}/stream"
            
            async with aiohttp.ClientSession() as session:
                form_data = aiohttp.FormData()
                form_data.add_field('audio', audio_data, content_type='audio/wav')
                form_data.add_field('dialect', self.dialect)
                
                async with session.post(asr_url, data=form_data, timeout=5) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        await self.send(text_data=json.dumps({
                            'type': 'partial_transcript',
                            'text': result.get('text', ''),
                            'confidence': result.get('confidence', 0.0),
                            'is_final': result.get('is_final', False)
                        }))
                    else:
                        logger.error(f"ASR service returned status {response.status}")
        
        except asyncio.TimeoutError:
            logger.error("ASR service timeout")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'ASR service timeout'
            }))
        except Exception as e:
            logger.error(f"Error processing audio chunk: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to process audio'
            }))
