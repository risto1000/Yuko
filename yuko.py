from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import os
from datetime import datetime
import shutil
import json

# set right address and path to file
SERVER_ADDRESS = '10.160.0.29'
PORT = 9999
FILENAME = "yuko.txt"

DELETE_MARKER = " [DELETED]"

def read_results():
    file = open(FILENAME, "r")
    results = {}
    games = []
    players = []
    for line in file:
        if DELETE_MARKER not in line:
            line = line.rstrip()
            splitted = line.split(',')
            game = {}
            for result in splitted:
                points = result.split(':')
                if not(points[0] in players):
                    players.append(points[0])
                game[points[0]] = int(points[1])
            games.append(game)
    
    file.close

    for player in players: results[player] = 0

    for game in games:
        values = list(game.values())
        values.sort()
        median = values[len(values) // 2]
        for player in players:
            if player in game:
                results[player] += game[player]
            else:
                results[player] += median

            if results[player] % 50 == 0 and results[player] > 0:
                results[player] = results[player] - 25

    return (results, games, players)

    
def print_results(results, games, players):
    print(f"Server online on http://{SERVER_ADDRESS}:{PORT}")
    print("  |", end='')
    for player in players:
        print(f" {player:>10} ",end='')
    print("")
    print("__|",end='')
    print(len(players) * 12 * "_")

    terminal_height = shutil.get_terminal_size().lines
    if len(games) > terminal_height - 8:
        i = len(games) - terminal_height + 8
    else:
        i = 0

    for i in range(i,len(games)):
        game = games[i]
        print(f"{i + 1:>2}|",end='')
        values = list(game.values())
        values.sort()
        median = values[len(values) // 2]
        for player in players:
            if player in game:
                print(f" {game[player]:10} ",end='')
            else:
                print(f"        ({median:2})",end='')
        print("")
        i += 1
    print("__|",end='')
    print(len(players) * 12 * "_")
    print(" =|",end='')
    for player in results:
        print(f" {results[player]:10} ",end='')
    print("")

def add_game(query, game_amount):
    try:
        for key in query:
            check = int(query[key][0])
        input = ""
        for key in query:
            input += f"{key}:{query[key][0]},"
        input = input[:-1]
        print((6 + game_amount) * "\033[F")
        with open(FILENAME, "r") as file:
            lines = file.readlines()
        with open(FILENAME, "w") as file:
            file.writelines(lines)
            file.write(f"{input}\n")
        return "Game added successfully\n"
    except OSError:
        print((6 + game_amount) * "\033[F")
        return "File unaccessible\n"
    except ValueError:
        print((6 + game_amount) * "\033[F")
        return f"Input not valid (after {check})\n"
    

def delete_last(game_amount, player_amount):
    try:
        print((6 + game_amount) * "\033[F")
        for i in range(5 + game_amount): 
            print((3 + player_amount * 12) * " ")
        print((7 + game_amount) * "\033[F")
        with open(FILENAME, "r") as file:
            lines = file.readlines()

        i = None
        for j in range(len(lines) - 1, -1, -1):
            if DELETE_MARKER not in lines[j]:
                i = j
                break

        if i is not None:
            lines[i] = lines[i].rstrip("\n") + DELETE_MARKER + "\n"
            with open(FILENAME, "w") as file:
                file.writelines(lines)
            return "Last game deleted\n"
        else:
            return "No games to delete\n"

    except OSError:
        return "File unaccessible\n"
    
def undo_delete(game_amount):
    try:
        print((6 + game_amount) * "\033[F")
        with open(FILENAME, "r") as file:
            lines = file.readlines()

        if lines and DELETE_MARKER in lines[len(lines) - 1]:
            i = None
            marked = False
            for j in range(len(lines) - 1, -1, -1):
                if DELETE_MARKER in lines[j]:
                    marked = True
                    if j == 0: i = j
                elif marked == True:
                    i = j + 1
                    break


        
            lines[i] = lines[i].replace(DELETE_MARKER, "")
            with open(FILENAME, "w") as file:
                file.writelines(lines)
            return "Undo successful\n"
        else:
            return "No deletion to undo\n"
        
    except OSError:
        return "File unaccessible\n"
    


def reset(game_amount, player_amount):
    try:
        terminal_height = shutil.get_terminal_size().lines
        print((5 + min(game_amount, terminal_height - 8)) * "\033[F")
        for i in range(5 + min(game_amount, terminal_height - 8)): 
            print((3 + player_amount * 12) * " ")
        print((7 + game_amount) * "\033[F")

        with open(FILENAME, "r") as file:
            lines = file.readlines()
        lines = [line for line in lines if DELETE_MARKER not in line]
        with open(FILENAME, "w") as file:
            file.writelines(lines)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(FILENAME)
        os.rename(FILENAME, f"{name}_{timestamp}{ext}")

        with open(FILENAME, "w") as file:
            pass
        return "Table reset\n"
    except OSError:
        return "File unaccessible\n"

class RequestHandler(BaseHTTPRequestHandler):
    (results, games, players) = read_results()
    print_results(results, games, players)

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        command = parsed_path.path.lstrip('/')

        if command =="get_players":
            (results, games, players) = read_results()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(players).encode())

        else:
            try:
                with open("yuko.html", "r") as file:
                    html_content = file.read()
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(html_content.encode('utf-8'))
            except FileNotFoundError:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"404 Not Found: The requested file does not exist.")

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        command = parsed_path.path.lstrip('/')
        query = urllib.parse.parse_qs(parsed_path.query)

        (results, games, players) = read_results()

        response = "Invalid command\n"
        if command == "add" and query:
            response = add_game(query, len(games))
            (results, games, players) = read_results()
            print_results(results, games, players)
        elif command == "delete":
            response = delete_last(len(games), len(players))
            (results, games, players) = read_results()
            print_results(results, games, players)
        elif command == "undo":
            response = undo_delete(len(games))
            (results, games, players) = read_results()
            print_results(results, games, players)
        elif command == "reset":
            response = reset(len(games), len(players))
            (results, games, players) = read_results()
            print_results(results, games, players)
        self.send_response(301)
        self.send_header('Location', '/')
        self.end_headers()


    def log_message(self, format, *args):
        return  # Suppress logging



def run(server_class=HTTPServer, handler_class=RequestHandler, port=PORT):
    server_address = (SERVER_ADDRESS, port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Server stopped.")

if __name__ == "__main__":
    run()