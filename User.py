'''User
In server_ip enter the IP address of CLU.
In case if you want to play the game in the same PC, server_ip='127.0.0.1' '''

import pygame as py
import socket
import sys
from network import send_json, recv_json

class GameClient:
    def __init__(self,server_ip='127.0.0.1',port=5555):
        #Setup
        py.init()
        self.width=800
        self.height=600
        self.TILE_SIZE=20
        self.cols=self.width//self.TILE_SIZE
        self.rows=self.height//self.TILE_SIZE
        self.screen=py.display.set_mode((self.width,self.height))
        py.display.set_caption("TRON Light Cycle Game")
        py.display.set_icon(py.image.load("logo_light_cycle.png"))
        self.clock=py.time.Clock()
        self.FPS=10
        # Inside __init__()
        py.mixer.init()
        py.mixer.music.load("audio/bgm_main.wav")
        py.mixer.music.set_volume(0.5)
        py.mixer.music.play(-1)  # Loop forever


        #Colors
        self.BLACK=(0,0,0)
        self.GRID_COLOR=(40,255,255)
        self.p1_color=(255,95,31)
        self.p2_color=(50,150,255)

        #Network
        self.server_ip=server_ip
        self.port=port
        self.conn=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.conn.connect((self.server_ip,self.port))
            print(f"[CLIENT] Connected to server at {self.server_ip}:{self.port}")
        except Exception as e:
            print(f"[CLIENT] Connection failed: {e}")
            sys.exit()

    def draw_grid(self):
        for x in range(0,self.width,self.TILE_SIZE):
            py.draw.line(self.screen,self.GRID_COLOR,(x,0),(x,self.height),1)
        for y in range(0,self.height,self.TILE_SIZE):
            py.draw.line(self.screen,self.GRID_COLOR,(0,y),(self.width,y),1)

    def get_input_dict(self, keys):
        return {
            "up":keys[py.K_UP],
            "down":keys[py.K_DOWN],
            "left":keys[py.K_LEFT],
            "right":keys[py.K_RIGHT]
        }

    def draw_trail(self,trail,color):
        for x, y in trail:
            rect=py.Rect(x*self.TILE_SIZE,y*self.TILE_SIZE,self.TILE_SIZE,self.TILE_SIZE)
            py.draw.rect(self.screen,color,rect)

    def show_result_screen(self,message):
        font=py.font.SysFont("Consolas",40)
        self.screen.fill(self.BLACK)
        py.mixer.music.stop()

        if message=="CLU Wins!":
            color=self.p1_color
            py.mixer.music.load("audio/bgm_clu_win.wav")
        elif message=="User Wins!":
            color=self.p2_color
            py.mixer.music.load("audio/bgm_user_win.wav")
        else:
            color=self.GRID_COLOR
        py.mixer.music.play()    
        text=font.render(message,True,color)
        self.screen.blit(text,((self.width-text.get_width())//2,self.height//2))
        py.display.update()
        py.time.wait(10000)
        py.mixer.music.stop()


    def run(self):
        try:
            initial=recv_json(self.conn)
            if not initial or initial.get("status")!="ready":
                print("[CLIENT] Server did not send ready state.")
                return
        except:
            print("[CLIENT] Error receiving initial state.")
            return

        running=True
        while running:
            self.clock.tick(self.FPS)
            self.screen.fill(self.BLACK)
            self.draw_grid()

            for event in py.event.get():
                if event.type==py.QUIT:
                    running=False

            keys=py.key.get_pressed()
            input_data=self.get_input_dict(keys)
            try:
                send_json(self.conn, input_data)
            except:
                print("[CLIENT] Failed to send input.")
                break

            try:
                game_state=recv_json(self.conn)
                if not game_state:
                    print("[CLIENT] Empty game state.")
                    break
            except:
                print("[CLIENT] Failed to receive game state.")
                break

            self.draw_trail(game_state.get("p1_trail", []), self.p1_color)
            self.draw_trail(game_state.get("p2_trail", []), self.p2_color)
            if "result" in game_state:
                self.show_result_screen(game_state["result"])
                break

            py.display.update()

        py.quit()
        self.conn.close()


client = GameClient(server_ip="127.0.0.1", port=5555) 
client.run()