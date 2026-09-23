import random
import time

class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.attempts = 0
        self.games_played = 0
        self.games_won = 0
        self.best_score = 0
        self.time_taken = 0.0

class GuessingGame:
    def __init__(self):
        self.leaderboard = {} 
        self.load_leaderboard()

    def display_rules(self):
        print("\n" + "=" * 45)
        print("          GAME RULES & SCORING")
        print("=" * 45)
        print("1. Players: 2 to 5 players per game.")
        print("2. Turn order is randomly shuffled.")
        print("3. Difficulties:")
        print("   - Easy:   1 to 50  (7 attempts)")
        print("   - Medium: 1 to 100 (6 attempts)")
        print("   - Hard:   1 to 500 (5 attempts)")
        print("4. Hints:")
        print("   - 'Very Close!' if within 5 of the secret number")
        print("   - Otherwise 'Too High!' or 'Too Low!'")
        print("5. Scoring:")
        print("   - Start with 100 base points")
        print("   - Penalty: -10 points for each wrong guess")
        print("   - Speed bonus: Extra points for guessing under 20 seconds")
        print("   - 0 points if you run out of attempts")
        print("=" * 45)

    def select_difficulty(self):
        print("\nSelect Difficulty:")
        print("1. Easy (1-50, 7 attempts)")
        print("2. Medium (1-100, 6 attempts)")
        print("3. Hard (1-500, 5 attempts)")
        
        while True:
            ch = input("Enter choice (1-3): ").strip()
            if ch == "1":
                return 1, 50, 7
            elif ch == "2":
                return 1, 100, 6
            elif ch == "3":
                return 1, 500, 5
            else:
                print("Invalid difficulty choice! Please choose 1, 2, or 3.")

    def get_hint(self, guess, secret):
        diff = abs(guess - secret)
        if diff <= 5:
            if guess > secret:
                return "Very Close! (A little high)"
            else:
                return "Very Close! (A little low)"
        elif guess > secret:
            return "Too High!"
        else:
            return "Too Low!"

    def play_round(self, player, min_val, max_val, max_attempts):
        secret_number = random.randint(min_val, max_val)
        attempts_used = 0
        guessed_correctly = False

        print(f"\n>>> {player.name}'s Turn! <<<")
        print(f"I'm thinking of a number between {min_val} and {max_val}.")
        print(f"You have {max_attempts} attempts. Timer starts now!")

        start_time = time.time()

        while attempts_used < max_attempts:
            remaining = max_attempts - attempts_used
            guess_input = input(f"Attempt {attempts_used + 1}/{max_attempts} (Remaining: {remaining}) - Enter guess: ").strip()

            # Exception handling for non-numeric input
            try:
                guess = int(guess_input)
            except ValueError:
                print("Invalid input! Please enter a valid whole number.")
                continue
            if guess < min_val or guess > max_val:
                print(f"Please guess within range {min_val} to {max_val}!")
                continue

            attempts_used += 1

            if guess == secret_number:
                end_time = time.time()
                time_taken = round(end_time - start_time, 2)
                print(f"\nBINGO! Correct guess in {attempts_used} attempt(s) and {time_taken}s!")

              
                wrong_attempts = attempts_used - 1
                round_score = 100 - (wrong_attempts * 10)

             
                time_bonus = 0
                if time_taken < 20:
                    time_bonus = int((20 - time_taken) * 2)
                    print(f"Speed Bonus: +{time_bonus} points!")

                total_round_score = round_score + time_bonus

                player.attempts = attempts_used
                player.time_taken = time_taken
                player.score = total_round_score
                guessed_correctly = True
                break
            else:
                hint = self.get_hint(guess, secret_number)
                print(f"Hint: {hint}")

        if not guessed_correctly:
            print(f"\nOut of attempts! The secret number was {secret_number}.")
            print("Score: 0 points for this game.")
            player.attempts = max_attempts
            player.time_taken = 0.0
            player.score = 0

        return player.score

    def start_new_game(self):
        print("\n--- START NEW GAME ---")

       
        while True:
            num_input = input("Enter number of players (2 to 5): ").strip()
            try:
                num_players = int(num_input)
                if 2 <= num_players <= 5:
                    break
                else:
                    print("Number of players must be between 2 and 5.")
            except ValueError:
                print("Invalid input! Please enter a number.")

        current_players = []
        names_taken = set()

        for i in range(1, num_players + 1):
            while True:
                name = input(f"Enter name for Player {i}: ").strip()
                if not name:
                    print("Name cannot be empty!")
                    continue
                if name.lower() in names_taken:
                    print(f"Name '{name}' is already taken! Please enter a unique name.")
                    continue
                names_taken.add(name.lower())

         
                if name in self.leaderboard:
                    p = self.leaderboard[name]
                else:
                    p = Player(name)
                    self.leaderboard[name] = p

                current_players.append(p)
                break

      
        min_val, max_val, max_attempts = self.select_difficulty()

      
        random.shuffle(current_players)
        print("\nTurn order randomly chosen:")
        for idx, p in enumerate(current_players, 1):
            print(f"  Turn {idx}: {p.name}")


        round_results = []
        for p in current_players:
            score = self.play_round(p, min_val, max_val, max_attempts)
            round_results.append((p.name, score, p.attempts, p.time_taken))

            p.games_played += 1
            if score > p.best_score:
                p.best_score = score

        round_results.sort(key=lambda x: x[1], reverse=True)
        winner_name = round_results[0][0]
        top_score = round_results[0][1]

        if top_score > 0:
            self.leaderboard[winner_name].games_won += 1
            print(f"\n WINNER: {winner_name} with {top_score} points! ")
        else:
            print("\nNo one guessed correctly this round! Tied with 0 points.")

        print("\nRound Summary:")
        print(f"{'Rank':<5} | {'Player':<15} | {'Score':<8} | {'Attempts':<10} | {'Time (s)':<8}")
        print("-" * 55)
        for rank, res in enumerate(round_results, 1):
            print(f"{rank:<5} | {res[0]:<15} | {res[1]:<8} | {res[2]:<10} | {res[3]:<8}")

 
        self.save_leaderboard()

    def show_leaderboard(self):
        print("\n" + "=" * 55)
        print("               LEADERBOARD")
        print("=" * 55)

        if not self.leaderboard:
            print("Leaderboard is empty. Play a game first!")
            return

        sorted_players = sorted(
            self.leaderboard.values(),
            key=lambda p: (p.best_score, p.games_won),
            reverse=True
        )

        print(f"{'Rank':<5} | {'Player':<15} | {'Best Score':<12} | {'Won':<6} | {'Played':<6}")
        print("-" * 55)
        for rank, p in enumerate(sorted_players, 1):
            print(f"{rank:<5} | {p.name:<15} | {p.best_score:<12} | {p.games_won:<6} | {p.games_played:<6}")
        print("=" * 55)

    def search_player_stats(self):
        print("\n--- SEARCH PLAYER STATS ---")
        name = input("Enter player name: ").strip()

        found = None
        for p_name, p in self.leaderboard.items():
            if p_name.lower() == name.lower():
                found = p
                break

        if found:
            print("\nPlayer Statistics:")
            print(f"Name         : {found.name}")
            print(f"Best Score   : {found.best_score}")
            print(f"Games Played : {found.games_played}")
            print(f"Games Won    : {found.games_won}")
            win_rate = (found.games_won / found.games_played * 100) if found.games_played > 0 else 0
            print(f"Win Rate     : {win_rate:.1f}%")
        else:
            print(f"Player '{name}' not found in leaderboard.")

    def save_leaderboard(self):
        try:
            with open("leaderboard.txt", "w") as f:
                for p in self.leaderboard.values():
                    f.write(f"{p.name}|{p.best_score}|{p.games_played}|{p.games_won}\n")
        except IOError:
            print("Error saving leaderboard.")

    def load_leaderboard(self):
        try:
            with open("leaderboard.txt", "r") as f:
                for line in f:
                    parts = line.strip().split("|")
                    if len(parts) == 4:
                        p = Player(parts[0])
                        p.best_score = int(parts[1])
                        p.games_played = int(parts[2])
                        p.games_won = int(parts[3])
                        self.leaderboard[p.name] = p
        except FileNotFoundError:
            pass

    def menu(self):
        while True:
            print("\n==========================================")
            print(" MULTIPLAYER NUMBER GUESSING CHAMPIONSHIP")
            print("==========================================")
            print("1. Start New Game")
            print("2. Display Rules")
            print("3. Show Leaderboard")
            print("4. Search Player Statistics")
            print("5. Exit")
            print("==========================================")

            ch = input("Enter choice (1-5): ").strip()

            if ch == "1":
                self.start_new_game()
            elif ch == "2":
                self.display_rules()
            elif ch == "3":
                self.show_leaderboard()
            elif ch == "4":
                self.search_player_stats()
            elif ch == "5":
                self.save_leaderboard()
                print("Thanks for playing! Goodbye.")
                break
            else:
                print("Invalid menu choice! Please select between 1 and 5.")

if __name__ == "__main__":
    GuessingGame().menu()
