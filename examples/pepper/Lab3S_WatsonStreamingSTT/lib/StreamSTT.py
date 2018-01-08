# Copyright 2017 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This is a generic Watson speech-to-text streaming client using ws4py websockets API
# It uses the Linux arecord command to get an audio stream

import os, sys, time, ssl, traceback

from ws4py.client.threadedclient import WebSocketClient

# The version goes into the log so that we know which is actually loaded
WatsonSTTWebSocketClient_VERSION = "1.0"
WatsonSTTWebSocketClient_URL ="wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize"

# This class manages the funelling of arecord raw audio data to Watson STT Streaming websocket API
class WatsonSTTWebSocketClient(WebSocketClient):
    def received_transcript(self,final,confidence,transcript):
        """ Default implementation for the transcript call-back, should be overridden """
        self.info("{0} {1} {2}".format(final,confidence,transcript))

    def info(self,msg):
        """  This is intended to be overidden by subclasses to implement logging """
        print msg
        
    # Constructor with audio datarate as parameter
    def __init__(self,watsonSTTUsername,watsonSTTPassword,rate=16000,bits=16,buflen=1024,model="en-US_BroadbandModel",timeout=-1,audioFilename=None,progressPipe=None):            
        # Store parameters to instance vars
        self.rate=rate
        self.bits=bits
        self.buflen=buflen
        self.model=model   # default is en-US_BroadbandModel
        self.audioFilename=os.path.splitext(audioFilename) if audioFilename else None
        self.timeout=timeout  # Will cause
        self.progressPipe=progressPipe
        
        # Handles
        self.arecordproc=None
        self.audioF=None
                
        # state variables
        self.listening=False
        self.suspended=False

        self.info("WatsonSTTWebSocketClient VERSION {0}".format(WatsonSTTWebSocketClient_VERSION))        
        try:
            ws_url=WatsonSTTWebSocketClient_URL
            if self.model:
                ws_url=ws_url + ("?model={0}".format(self.model))
            
            # Make the basic authentication header string
            import base64
            authString = "%s:%s" % (watsonSTTUsername, watsonSTTPassword)
            base64Auth = base64.encodestring(authString).replace("\n", "")
            
            self.info("Init WebSocketClient to {0} with {1}".format(ws_url,authString))
            WebSocketClient.__init__(self, ws_url,
                headers=[("Authorization", "Basic %s" % base64Auth),("model",self.model)])
            self.connect()
        except:
            self.info("Failed to open WebSocketClient.")
            raise

    def sendSTT_StartCommand(self):
        """ Start the STT API """
        command='{{"action": "start", ' +\
                '"content-type": "audio/l{0};rate={1};endianness=little-endian", ' +\
                '"word_confidence" : true, ' +\
                '"timestamps" : true, '+\
                '"interim_results": true, '+\
                '"inactivity_timeout" : {2}}}'
        command=command.format(self.bits,self.rate,self.timeout)
        self.info("WebSocketClient.opened, starting STT with {0}".format(command))
        self.send(command)
    
    def sendSTT_StopCommand(self):
        """ Stop the STT API """
        command='{"action": "stop"}'
        self.info("WebSocketClient.opened, stopping STT ")
        self.send(command)    
            
    def suspendListen(self):
        if not self.suspended:
            self.suspended=True;
            self.sendSTT_StopCommand()
                
    def resumeListen(self):
        if self.suspended:
            self.suspended=False;
            self.sendSTT_StartCommand()

    # WebSocketClient call-back
    def opened(self):
        self.info("WebSocketClient.opened")

        # Starting the audio streaming thread
        self.info("Starting stream_audio thread")
        import threading
        self.stream_audio_thread = threading.Thread(target=self.stream_audio)
        self.stream_audio_thread.start()

        # Start the STT
        self.sendSTT_StartCommand()
        
    # WebSocketClient call-back
    def received_message(self, message):
        try:
            # Convert the message string to json
            import json
            message = json.loads(str(message))
        
            if "state" in message:
                state=message["state"]
                if state == "listening":
                    self.info("STT Listening started")
                    self.listening = True
                    self.suspended = False
                else :
                    self.info("Unhandled state {0}".format(state))
            elif "error" in message:
                error=message["error"]
                self.info("STT Error {0}".format(error))
            elif "results" in message:
                final=None
                transcript=None
                confidence=None
            
                results=message["results"]
                #self.info("results={0}".format(results))
                for result in results:
                    #self.info("result={0}".format(result))
                    if "final" in result:
                        final=result["final"]
                    if "alternatives" in result:
                        alternatives=result["alternatives"]
                        for alternative in alternatives:
                            #self.info("alternative= {0}".format(alternative))
                            if "transcript" in alternative:
                                transcript=alternative["transcript"]
                            if "confidence" in alternative:
                                confidence=alternative["confidence"]
                #if final and transcript and confidence:
                self.received_transcript(final,confidence,transcript)
            else:
                self.info("unknown message received: {0}".format(message))
        except Exception as exc:
            self.info("STT Exception {0}".format(exc))
        except Error as err:
            self.info("STT Error {0}".format(err))
        except:
            self.info("STT Uncaugh exception")

    # WebSocketClient call-back
    def closed(self,code,reason):
        self.info("WebSocketClient.closed, code={0}, reason={1}".format(code,reason))
        
    # WebSocketClient override
    def close(self,code,reason):
        self.info("closed code={0} reason={1}".format(code,reason))
                
        # If there is an audio streaming thread, wait for it to complete
        if self.stream_audio_thread:
            # cause the connection to close
            self.info("Stopping audio streaming thread")
            self.listening = False
    
            # wait for audio thread to complete
            self.stream_audio_thread.join()
            self.stream_audio_thread=None
            
        self.info("Closing WebSocketClient")
        WebSocketClient.close(self,code,reason)
        
        if self.audioF:
            self.info("Closing audio recording {0}.{1} file at position {2}".format(self.audioFilename[0],self.audioFilename[1],self.audioF.tell()))
            self.audioF.close()
            self.audioF=None

    def stream_audio(self):
        """ Streaming audio listening thread """
        # Wait for the STT to be available
        while not self.listening:
            time.sleep(0.1)

        # Start the audio capture subprocess
        import subprocess
        reccmd = ["arecord", "-f", "S{0}_LE".format(self.bits), "-r", str(self.rate), "-t", "raw"]
        self.info("Starting subprocess: {0}".format(reccmd))
        self.arecordproc = subprocess.Popen(reccmd, stdout=subprocess.PIPE)
        
        # If there is a aufio file name, record to file as well
        if self.audioFilename:
            import wave
            self.audioF=wave.open("{0}_{2}.{1}".format(self.audioFilename[0],self.audioFilename[1],time.time()), 'wb')
            self.audioF.setnchannels(1)
            self.audioF.setsampwidth(self.bits/8)
            self.audioF.setframerate(self.rate)

        # Main audio streaming loop
        while self.listening:
            if self.progressPipe: self.progressPipe.write('.')
            
            # Get the audio data from arecord
            data = self.arecordproc.stdout.read(self.buflen)
            if self.progressPipe:
                if self.buflen == len(data):
                    self.progressPipe.write("_")
                else:
                    self.progressPipe.write("!")
                self.progressPipe.flush()
                
            # Don't send audio data while suspended
            if not self.suspended:
                binData=bytearray(data)
                if self.audioF:
                    self.audioF.writeframesraw(binData)
                
                try: 
                    self.send(binData, binary=True)
                except ssl.SSLError as exc:
                    self.info("SSL Error {0}".format(exc))
                    pass
                    
        # Terminate the arecord subprocess instance
        if self.arecordproc:
            self.arecordproc.kill()
            self.arecordproc=None

# Stand-alone test entry point        
if __name__ == '__main__':
    if len(sys.argv)>1:
        try:
            print "Testing Watson Speech-to-text"
            stt_client=None
            #stt_client = SpeechToTextClient(sys.argv[1],sys.argv[2],audioFilename = 'audio{0}.wav'.format(time.time()),progressPipe=sys.stdout)
            stt_client = WatsonSTTWebSocketClient(sys.argv[1],sys.argv[2])
            print "Waiting for keyboard line input or Ctrl-C"
            c=raw_input()
            print "Stopped from keyboard"
        except KeyboardInterrupt as kbd:
            print "Stopped from Ctrl-C"
        except:
            print "Exception:", sys.exc_info()[0], sys.exc_info()[1]
            traceback.print_exc(file=sys.stdout)
            raise          
        finally:
            if stt_client:
                stt_client.close(0,"OK")