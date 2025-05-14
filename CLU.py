#CLU
import pygame as py
import socket
import sys
from network import send_json, recv_json
from player import Player

class GameServer:
    def __init__(self, host='0.0.0.0', port=5555):  #host='0.0.0.0' is for accepting all IP addresses
        #Setup
        py.init()
        self.width=800
        self.height=600
        self.TILE_SIZE=20
        self.cols=self.width//self.TILE_SIZE
        self.rows=self.height//self.TILE_SIZE
        self.screen=py.display.set_mode((self.width, self.height))
        py.display.set_caption("TRON Light Cycle Game")
        py.display.set_icon(py.image.load("logo_light_cycle.png"))
        self.clock=py.time.Clock()
        self.FPS=10

        #Colors
        self.BLACK=(0,0,0)
        self.GRID_COLOR=(40,255,255)
        self.ORANGE=(255,95,31)
        self.BLUE=(50,150,255)

        #Network
        self.host=host
        self.port=port
        self.client_conn=None

        #Players: CLU=p1, User=p2
        self.players=[
            Player(5,5,(self.ORANGE), direction="RIGHT"),      #CLU
            Player(self.cols-6,self.rows-6,(self.BLUE), direction="LEFT")  #User
        ]
        self.remote_keys = {}

    def wait_for_client(self):
        font=py.font.SysFont("Consolas", 40)
        self.screen.fill(self.BLACK)
        text=font.render("Waiting for User...",True,self.GRID_COLOR)
        self.screen.blit(text,((self.width-text.get_width())//2,self.height//2))
        py.display.update()

        print(f"[SERVER] Waiting for connection on {self.host}:{self.port}")
        server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(1)
        self.client_conn, addr = server_socket.accept()
        print(f"[SERVER] Client connected from {addr}")

    def draw_grid(self):
        for x in range(0,self.width,self.TILE_SIZE):
            py.draw.line(self.screen,self.GRID_COLOR,(x,0),(x,self.height),1)
        for y in range(0,self.height, self.TILE_SIZE):
            py.draw.line(self.screen, self.GRID_COLOR,(0,y),(self.width,y),1)

    def handle_remote_input(self):
        try:
            self.remote_keys = recv_json(self.client_conn)
        except:
            print("[SERVER] Failed to receive client input.")
            self.remote_keys = {}

    def show_result_screen(self,message,color):
        font = py.font.SysFont("Consolas", 40)
        self.screen.fill(self.BLACK)
        text = font.render(message,True,color)
        self.screen.blit(text,((self.width-text.get_width())//2,self.height//2))
        py.display.update()
        py.time.wait(10000)  #Shows for 10 seconds


    def run(self):
        self.wait_for_client()
        try:
            send_json(self.client_conn, {"status": "ready"})
        except:
            print("[SERVER] Failed to send initial message.")
            return

        running = True
        while running:
            self.clock.tick(self.FPS)
            self.screen.fill(self.BLACK)
            self.draw_grid()

            for event in py.event.get():
                if event.type==py.QUIT:
                    running=False

            #Input handling
            keys=py.key.get_pressed()
            self.players[0].handle_input({
                "up":keys[py.K_w],
                "down":keys[py.K_s],
                "left":keys[py.K_a],
                "right":keys[py.K_d]
            })

            self.handle_remote_input()
            self.players[1].handle_input(self.remote_keys)

            #Game logic
            all_trails=set()
            for player in self.players:
                if player.alive:
                    all_trails.update(player.trail)

            for player in self.players:
                if player.alive:
                    player.move()
                    player.check_collision(self.cols,self.rows,all_trails)
                    player.draw(self.screen,self.TILE_SIZE)

                if not self.players[0].alive and self.players[1].alive:
                    winner = "User Wins!"
                    running = False
                    color=self.BLUE
                elif not self.players[1].alive and self.players[0].alive:
                    winner = "CLU Wins!"
                    running = False
                    color=self.ORANGE
                elif not self.players[0].alive and not self.players[1].alive:
                    winner = "Draw!"
                    running = False

            try:
                send_json(self.client_conn, {
                    "p1_trail":self.players[0].trail,
                    "p2_trail":self.players[1].trail
                })
            except:
                print("[SERVER] Client disconnected.")
                break

            py.display.update()
        try:
            send_json(self.client_conn,{"result":winner})
        except:
            print("[SERVER] Failed to send result.")

        self.show_result_screen(winner,color)

        py.quit()
        if self.client_conn:
            self.client_conn.close()
        sys.exit()

server = GameServer()
server.run()
