from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import time

def read_results():
    file = open("yuko.txt", "r")
    results = {}
    games = []
    players = []
    for line in file:
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

    return (results, games, players)

    
def print_results(results, games, players):
    print("  |", end='')
    for player in players:
        print(f" {player:>10} ",end='')
    print("")
    print("__|",end='')
    print(len(players) * 12 * "_")
    i = 1
    for game in games:
        print(f"{i:>2}|",end='')
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
        print((5 + game_amount) * "\033[F")
        with open("yuko.txt", "r") as file:
            lines = file.readlines()
        with open("yuko.txt", "w") as file:
            file.writelines(lines)
            file.write(f"{input}\n")
        return "Game added successfully\n"
    except OSError:
        print((5 + game_amount) * "\033[F")
        return "File unaccessible\n"
    except ValueError:
        print((5 + game_amount) * "\033[F")
        return f"Input not valid (after {check})\n"
    

def delete_last(game_amount, player_amount):
    try:
        print((5 + game_amount) * "\033[F")
        for i in range(5 + game_amount): 
            print((3 + player_amount * 12) * " ")
        print((6 + game_amount) * "\033[F")
        with open("yuko.txt", "r") as file:
            lines = file.readlines()
        if lines:
            lines = lines[:-1]
            with open("yuko.txt", "w") as file:
                file.writelines(lines)
        return "Last game deleted\n"
    except OSError:
        return "File unaccessible\n"

def reset(game_amount, player_amount):
    try:
        print((5 + game_amount) * "\033[F")
        for i in range(5 + game_amount): 
            print((3 + player_amount * 12) * " ")
        print((6 + game_amount) * "\033[F")
        with open("yuko.txt", "w") as file:
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
        elif command == "reset":
            response = reset(len(games), len(players))
            (results, games, players) = read_results()
            print_results(results, games, players)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

    def log_message(self, format, *args):
        return  # Suppress logging



def run(server_class=HTTPServer, handler_class=RequestHandler, port=9999):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Server stopped.")

if __name__ == "__main__":
    run()