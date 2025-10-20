"""game launcher"""
import os
import sys
import json
import copy
import random
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from rich.prompt import Prompt
from rich_menu import Menu

NOSAVETODISK = False
CARDS: List[Dict[str, Any]] = []
SCROLLS: List[Dict[str, Any]] = []
ENEMIES: List[Dict[str, Any]] = []
SAVE = {}
SAVE_PATH = ""

console = Console()

def load_game_data():
    """load cards, scrolls, and enemies from JSON files"""
    global CARDS, SCROLLS, ENEMIES
    
    try:
        with open("cards.json", "r", encoding="utf-8") as f:
            CARDS = json.load(f)
    except FileNotFoundError:
        console.print("Warning: cards.json not found!", style="bold red")
    except json.JSONDecodeError as e:
        console.print(f"Error loading cards.json: {e}", style="bold red")
    
    try:
        with open("scrolls.json", "r", encoding="utf-8") as f:
            SCROLLS = json.load(f)
    except FileNotFoundError:
        console.print("Warning: scrolls.json not found!", style="bold red")
    except json.JSONDecodeError as e:
        console.print(f"Error loading scrolls.json: {e}", style="bold red")
    
    try:
        with open("enemies.json", "r", encoding="utf-8") as f:
            ENEMIES = json.load(f)
    except FileNotFoundError:
        console.print("Warning: enemies.json not found!", style="bold red")
    except json.JSONDecodeError as e:
        console.print(f"Error loading enemies.json: {e}", style="bold red")

def get_save_directory():
    """Get the path to the save directory (~/.scrollbound/runs)"""
    save_dir = Path.home() / ".scrollbound" / "runs"
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir

TEMPLATESAVE = {
    "hp": 30,
    "max_hp": 30,
    "tp": 2,
    "max_tp": 2,
    "gold": 0,
    "effects": [],
    "floor": 0,
    "biome": "cave",
    "hand": [],
    "stockpile": []
}

if NOSAVETODISK:
    console.print("!! Saving to disk has been disabled in this enviornment !!", style="bold red",
                  justify="center")
    mainMenu = Menu(
        "New Run",
        "Exit",
        title="S C R O L L B O U N D",
        color="bold blue",
        highlight_color="bold white",
    )
else:
    mainMenu = Menu(
        "New Run",
        "Continue Run", 
        "Exit",
        title="S C R O L L B O U N D",
        color="bold blue",
        highlight_color="bold white",
    )

load_game_data()

def save_game(savepath: str):
    """Save the current game state"""
    # no shit sherlock
    with open(savepath, "w", encoding="utf-8") as savefile:
        json.dump(SAVE, savefile, indent=2)

def scroll_shop():
    """Shop that appears every 5 floors - sells 3 random scrolls"""
    console.print("=== SCROLL SHOP ===", style="bold yellow")
    console.print(f"Gold: {SAVE.get('gold', 0)}", style="yellow")
    
    # grab 3 random scrolls
    sample_size = min(3, len(SCROLLS))
    scroll_options = random.sample(SCROLLS, k=sample_size)
    
    while True:
        # cum
        result = os.system('cls' if os.name == 'nt' else 'clear')
        if result != 0:
            console.clear()
        
        console.print("=== SCROLL SHOP ===", style="bold yellow")
        console.print(f"Gold: {SAVE.get('gold', 0)}", style="yellow")
        console.print()
        
        # here, good sir, pick one
        for i, scroll in enumerate(scroll_options, 1):
            string = f"{i}. "
            string += f"[bold blue]{scroll.get('name')}[/bold blue]\n"
            string += f"   [bright_black]{scroll.get('description')}[/bright_black]\n"
            string += f"   [yellow]{scroll.get('tp')}TP - Cost: {scroll.get('cost', 0)} gold[/yellow]"
            console.print(string)
        
        console.print()
        
        # create le menu
        menu_options = [str(i) for i in range(1, len(scroll_options) + 1)]
        menu_options.append("Leave Shop")
        
        shop_menu = Menu(
            *menu_options,
            title="What would you like to buy?",
            color="bold yellow",
            highlight_color="bold white"
        )
        
        choice = shop_menu.ask(screen=False, esc=False)
        
        if choice == "Leave Shop":
            break
        
        # buy scroll? please? im poor
        scroll_index = int(choice) - 1
        chosen_scroll = scroll_options[scroll_index]
        cost = chosen_scroll.get('cost', 0)
        
        if SAVE.get('gold', 0) >= cost:
            SAVE['gold'] -= cost
            SAVE['hand'].append(copy.deepcopy(chosen_scroll))
            console.print(f"Purchased {chosen_scroll.get('name')}!", style="bold green")
            scroll_options.pop(scroll_index)  # WOOHOO
            if not scroll_options:  # oh it's all gone, thanks i guess?
                console.print("The shop is sold out!", style="bold yellow")
                Prompt.ask("Press Enter to continue...")
                break
            Prompt.ask("Press Enter to continue...")
        else:
            console.print("Not enough gold!", style="bold red")
            Prompt.ask("Press Enter to continue...")

def voucher_shop():
    """Shop that appears every 10 floors - sells vouchers"""
    console.print("=== VOUCHER SHOP ===", style="bold magenta")
    console.print(f"Gold: {SAVE.get('gold', 0)}", style="yellow")
    
    while True:
        # cum
        result = os.system('cls' if os.name == 'nt' else 'clear')
        if result != 0:
            console.clear()
        
        console.print("=== VOUCHER SHOP ===", style="bold magenta")
        console.print(f"Gold: {SAVE.get('gold', 0)}", style="yellow")
        console.print()
        
        # display vouchers
        console.print("1. [bold red]TP Voucher[/bold red]")
        console.print("   [bright_black]Permanently increases maximum TP by 1[/bright_black]")
        console.print("   [yellow]Cost: 50 gold[/yellow]")
        console.print()
        
        console.print("2. [bold green]HP Voucher[/bold green]")
        console.print("   [bright_black]Permanently increases maximum HP by 3[/bright_black]")
        console.print("   [yellow]Cost: 50 gold[/yellow]")
        console.print()
        
        voucher_menu = Menu(
            "1",
            "2", 
            "Leave Shop",
            title="What would you like to buy?",
            color="bold magenta",
            highlight_color="bold white"
        )
        
        choice = voucher_menu.ask(screen=False, esc=False)
        
        if choice == "Leave Shop":
            break
        elif choice == "1":  # TP Voucher
            if SAVE.get('gold', 0) >= 50:
                SAVE['gold'] -= 50
                SAVE['max_tp'] = SAVE.get('max_tp', 2) + 1
                SAVE['tp'] = SAVE.get('max_tp', 3)  # refill toilet paper
                console.print("Purchased TP Voucher! Maximum TP increased by 1!", style="bold green")
                Prompt.ask("Press Enter to continue...")
            else:
                console.print("Not enough gold!", style="bold red")
                Prompt.ask("Press Enter to continue...")
        elif choice == "2":  # HP Voucher  
            if SAVE.get('gold', 0) >= 50:
                SAVE['gold'] -= 50
                SAVE['max_hp'] = SAVE.get('max_hp', 30) + 3
                SAVE['hp'] = SAVE.get('max_hp', 33)  # refill HP
                console.print("Purchased HP Voucher! Maximum HP increased by 3!", style="bold green")
                Prompt.ask("Press Enter to continue...")
            else:
                console.print("Not enough gold!", style="bold red")
                Prompt.ask("Press Enter to continue...")

def entry(inputsavepath: str):
    """entry point for the game"""
    global SAVE, SAVE_PATH
    SAVE_PATH = inputsavepath
    savepath = inputsavepath
    if not os.path.exists(savepath):
        raise FileNotFoundError(f"Save file {savepath} does not exist.")
    with open(savepath, "r", encoding="utf-8") as savefile:
        SAVE = json.load(savefile)
    if SAVE["floor"] == 0:
        def pick_cards():
            # get random cards (up to 5, or all available if fewer)
            sample_size = min(5, len(CARDS))
            options: List[Dict[str, Any]] = random.sample(CARDS, k=sample_size)
            # format options for display
            choice_options = []

            def show_cards():
                choice_options.clear()  # Clear the list before rebuilding it
                for opt in options:
                    # start with empty string
                    string = ""
                    # add bold blue name
                    string += f"[bold blue]{opt.get('name')}[/bold blue]\n"
                    # add gray description
                    string += f"[bright black]{opt.get('description')}[/bright black]\n"
                    # add yellow tp cost
                    string += f"[yellow]{str(opt.get('tp'))}TP[/yellow]"
                    # a
                    console.print(string)
                    choice_options.append(opt.get('name'))

            # remove one instance of the chosen card from options
            def pick_card_menu():
                # console.clear() is finnicky, so try the more robust:
                result = os.system('cls' if os.name == 'nt' else 'clear')
                if result != 0:
                    # and if that doesn't work, then we'll use it
                    console.clear()
                show_cards()
                choose_card_menu = Menu(
                    *sorted(choice_options),
                    title="^ Choose a starting card ^",
                    color="bold blue"
                )
                chosen_card = choose_card_menu.ask(screen = False, esc = False)
                for i, opt in enumerate(options):
                    if opt.get("name") == chosen_card:
                        SAVE["hand"].append(opt)
                        options.pop(i)
                        choice_options.remove(chosen_card)
                        break

            # pick first card
            pick_card_menu()
            # pick second card if possible
            if len(options) > 0:
                pick_card_menu()
        def pick_scrolls():
            # get random cards (up to 5, or all available if fewer)
            sample_size = min(5, len(SCROLLS))
            options: List[Dict[str, Any]] = random.sample(SCROLLS, k=sample_size)
            # format options for display
            choice_options = []

            def show_scrolls():
                choice_options.clear()  # Clear the list before rebuilding it
                for opt in options:
                    # start with empty string
                    string = ""
                    # add bold blue name
                    string += f"[bold blue]{opt.get('name')}[/bold blue]\n"
                    # add gray description
                    string += f"[bright black]{opt.get('description')}[/bright black]\n"
                    # add yellow tp cost
                    string += f"[yellow]{str(opt.get('tp'))}TP[/yellow]"
                    # a
                    console.print(string)
                    choice_options.append(opt.get('name'))

            # remove one instance of the chosen card from options
            def pick_scroll_menu():
                # console.clear() is finnicky, so try the more robust:
                result = os.system('cls' if os.name == 'nt' else 'clear')
                if result != 0:
                    # and if that doesn't work, then we'll use it
                    console.clear()
                show_scrolls()
                choose_card_menu = Menu(
                    *sorted(choice_options),
                    title="^ Choose a starting scroll ^",
                    color="bold blue"
                )
                chosen_card = choose_card_menu.ask(screen = False, esc = False)
                for i, opt in enumerate(options):
                    if opt.get("name") == chosen_card:
                        SAVE["hand"].append(opt)
                        options.pop(i)
                        choice_options.remove(chosen_card)
                        break

            # pick first scroll
            pick_scroll_menu()
            # pick second scroll if possible
            if len(options) > 0:
                pick_scroll_menu()
                # pick third scroll if possible
                if len(options) > 0:
                    pick_scroll_menu()

        pick_cards()
        pick_scrolls()
        SAVE["floor"] += 1
        # save the updated game state
        with open(savepath, "w", encoding="utf-8") as savefile:
            json.dump(SAVE, savefile, indent=2)

    descend()

def build_enemies() -> List[Dict[str, Any]]:
    """Generate enemies for the current floor"""
    potential_enemies = []
    enemies = []
    for enemy in ENEMIES:
        if enemy.get("from", 0) <= SAVE["floor"]: 
            potential_enemies.append(enemy)
    if not potential_enemies:
        SAVE["floor"] += 1
        return build_enemies()

    # add first anemone
    first_enemy = random.choice(potential_enemies)
    enemies.append(copy.deepcopy(first_enemy))

    # 25% chance to add another anemone
    if random.random() < 0.25:
        second_enemy = random.choice(potential_enemies)
        while second_enemy == first_enemy and len(potential_enemies) > 1:
            second_enemy = random.choice(potential_enemies)
        enemies.append(copy.deepcopy(second_enemy))

        # further 25% chance to add a third anemone
        if random.random() < 0.25:
            third_enemy = random.choice(potential_enemies)
            while (third_enemy in (first_enemy, second_enemy)) and len(potential_enemies) > 2:
                third_enemy = random.choice(potential_enemies)
            enemies.append(copy.deepcopy(third_enemy))

    # wait that's not how you spell enemy
    # don't code at 1AM :tongue:
    #
    # also why does VSCode complain about trailing whitespaces if it's
    # the one putting them there
    #
    # https://www.youtube.com/watch?v=RSUEno09yHs

    return enemies

def build_effects(effects):
    """Format effects list for display"""
    finallist = []
    for effect in effects:
        effect_str = " - " + f"[{effect.get('style', 'bold white')}] "
        effect_str += effect.get('type', '???')
        effect_str += " " + str(effect.get('duration')) if effect.get('duration') or effect.get('duration') != 0 else ""
        effect_str += " [/" + effect.get('style', 'bold white') + "]"
        finallist.append(effect_str)
    return "".join(finallist)

def process_enemy_effects(enemies):
    """Process ongoing effects on enemies"""
    enemies_to_remove = []
    
    for enemy in enemies:
        effects_to_remove = []
        
        for effect in enemy.get('effects', []):
            if effect.get('type') == 'FIERY':
                enemy['hp'] -= 5
                console.print(f"{enemy.get('name')} takes 5 fire damage!", style="bold red")

            if effect.get('type') == 'ELECTRIFIED':
                has_wet = any(e.get('type') == 'WET' for e in enemy.get('effects', []))
                if has_wet:
                    enemy['hp'] -= 10
                    console.print(f"{enemy.get('name')} takes 10 shock damage from being wet and electrified!", style="bold yellow")

            # tick tock ho
            if not effect.get('duration') == 0:
                effect['duration'] -= 1
            if effect.get('duration', 0) <= 0:
                effects_to_remove.append(effect)
        
        # times up
        for effect in effects_to_remove:
            enemy['effects'].remove(effect)

        # pfffft kablamo
        if enemy.get('hp', 0) <= 0:
            enemies_to_remove.append(enemy)
            SAVE["gold"] += enemy.get("gold", 0)
    
    # pffft kablamo
    for enemy in enemies_to_remove:
        enemies.remove(enemy)

def process_player_effects():
    """Process ongoing effects on the player"""
    if 'effects' not in SAVE:
        SAVE['effects'] = []
    
    effects_to_remove = []
    
    for effect in SAVE.get('effects', []):
        if effect.get('type') == 'FIERY':
            SAVE['hp'] -= 5
            console.print(f"You take 5 fire damage from burning!", style="bold red")
        
        elif effect.get('type') == 'POISON':
            SAVE['hp'] -= 3
            console.print(f"You take 3 poison damage!", style="bold green")
        
        elif effect.get('type') == 'ELECTRIFIED':
            # bzzzzt
            has_wet = any(e.get('type') == 'WET' for e in SAVE.get('effects', []))
            if has_wet:
                SAVE['hp'] -= 8
                console.print(f"You take 8 shock damage from being wet and electrified!", style="bold yellow")
        
        elif effect.get('type') == 'SLIMY':
            # ew
            console.print(f"You feel slimy and gross!", style="bold green")
        
        # decrease duration
        if not effect.get('duration') == 0:
            effect['duration'] -= 1
        if effect.get('duration', 0) <= 0:
            effects_to_remove.append(effect)
    
    # remove expireds
    for effect in effects_to_remove:
        SAVE['effects'].remove(effect)
        console.print(f"The {effect.get('type', 'unknown')} effect wears off!", style="bright_black")

def process_enemy_attacks(enemies):
    """Let enemies attack the player"""
    for enemy in enemies:
        # no attacks? megamind
        attacks = enemy.get('attacks', [])
        if not attacks:
            continue
        
        # pick an attack
        chosen_attack = random.choice(attacks)
        attack_name = chosen_attack.get('name', 'Attack')
        attack_damage = chosen_attack.get('damage', 0)
        attack_effects = chosen_attack.get('effects', [])
        
        console.print(f"{enemy.get('name')} uses {attack_name}!", style="bold red")
        
        # pew pew
        if attack_damage > 0:
            SAVE['hp'] -= attack_damage
            console.print(f"You take {attack_damage} damage!", style="bold red")
        
        # hisssss
        if attack_effects:
            if 'effects' not in SAVE:
                SAVE['effects'] = []
            for effect in attack_effects:
                # aw man
                existing_effect = None
                for player_effect in SAVE['effects']:
                    if player_effect.get('type') == effect.get('type'):
                        existing_effect = player_effect
                        break
                
                if existing_effect:
                    # shiver me timbers
                    existing_effect['duration'] = max(existing_effect.get('duration', 0), effect.get('duration', 0))
                else:
                    # haha
                    SAVE['effects'].append(copy.deepcopy(effect))
                
                console.print(f"You are afflicted with {effect.get('type', 'unknown effect')}!", style="bold yellow")

def descend():
    """Main game loop - handles floor progression and combat"""
    while True:
        # build enemies for the floor
        enemies = build_enemies()

        # main combat loop
        while True:
            # cum on the screen rq (coinpon reference)
            result = os.system('cls' if os.name == 'nt' else 'clear')
            if result != 0:
                console.clear()

            # print enemies
            for enemy in enemies:
                if not enemy.get('effects'):
                    enemy['effects'] = []
                console.print(f"- [bold red]{enemy.get('name')}[/bold red] ({enemy.get('hp')}{build_effects(enemy.get('effects'))})", style="bold white")

            # print cards
            cards = SAVE.get("hand", [])
            for card in cards:
                string = ""
                string += f"[bold blue]{card.get('name')}[/bold blue]\n"
                string += f"[bright black]{card.get('description')}[/bright black]\n"
                string += f"[yellow]{str(card.get('tp'))}TP[/yellow]"
                console.print(string)

            # print player stats
            console.print(f"\n[blue]FLOOR: {SAVE.get('floor')}[/blue], [yellow]TP: {SAVE.get('tp', 0)}/{SAVE.get('max_tp', 0)}[/yellow], [green]HP: {SAVE.get('hp', 0)}/{SAVE.get('max_hp', 0)}[/green], EFFECTS: {build_effects(SAVE['effects'])}\n")

            # pick whatchu wanna do ho
            card_picker_menu = Menu(
                *sorted(str(i + 1) for i in range(len(SAVE.get("hand", [])))),
                "End Turn",
                title="What card will you use?",
                color="bold blue",
                highlight_color="bold white"
            )

            chosen_card = card_picker_menu.ask(screen=False, esc=False)

            # regen TP on end of turn
            if chosen_card == "End Turn":
                console.print("You end your turn.", style="bold white")
                SAVE["tp"] = SAVE.get("max_tp", 2)
                
                # chopped
                process_enemy_effects(enemies)
                
                # kablamo?
                if len(enemies) == 0:
                    console.print("You have defeated all enemies on this floor!", style="bold green")
                    SAVE["floor"] += 1
                    SAVE["tp"] = SAVE.get("max_tp", 2)
                    
                    # save game after each floor
                    save_game(SAVE_PATH)
                    
                    # check for shops
                    if SAVE["floor"] % 10 == 0:  # voucher shop every 10 floors
                        voucher_shop()
                        save_game(SAVE_PATH)  # save after shop
                    elif SAVE["floor"] % 5 == 0:  # scroll shop every 5 floors (not 10)
                        scroll_shop()
                        save_game(SAVE_PATH)  # save after shop
                    
                    Prompt.ask("Press Enter to continue...")
                    break # oh yeah bbg
                
                # enemies attack back!
                process_enemy_attacks(enemies)
                
                # process player effects (poison, burn, etc.)
                process_player_effects()
                
                # rip?
                if SAVE.get('hp', 0) <= 0:
                    console.print("You have been defeated!", style="bold red")
                    console.print("Game Over!", style="bold red")
                    Prompt.ask("Press Enter to continue...")
                    return  # rip.
                
                Prompt.ask("Press Enter to continue...")
                continue

            # get chosen card
            chosen_card = SAVE.get("hand", [])[int(chosen_card)-1]

            # check if player has enough TP
            if chosen_card.get("tp", 0) > SAVE.get("tp", 0):
                console.print("You do not have enough TP to play that card.", style="bold red")
                Prompt.ask("Press Enter to continue...")
                continue

            # card go brrrrrr
            SAVE["tp"] -= chosen_card.get("tp", 0)
            targets_remaining = chosen_card.get("targets", 1)

            # target 0 = nuke nuke! (starship troopers pinball ref)
            if chosen_card.get("targets", 1) == 0:
                enemies_to_remove = []
                for chosen_enemy in enemies:
                    # apply damage
                    chosen_enemy['hp'] -= chosen_card.get("damage", 0)

                    # and effects
                    if len(chosen_card.get("effects", [])) > 0:
                        if not chosen_enemy.get('effects'):
                            chosen_enemy['effects'] = []
                        for effect in chosen_card.get("effects", []):
                            if effect.get('type') == 'HEAL':
                                SAVE['hp'] += 5
                                effect['duration'] -= 1
                                console.print("You healed 5HP!", style="green")
                                if effect['duration'] != 0:
                                    SAVE['effects'].append(effect)
                            elif effect.get('type') == 'CLEANSE':
                                console.print("You cleansed yourself, removing all effects!", style="green")
                                SAVE['effects'] = []
                            elif effect not in chosen_enemy['effects']:
                                chosen_enemy['effects'].append(effect)

                    # kablamo
                    if chosen_enemy['hp'] <= 0:
                        enemies_to_remove.append(chosen_enemy)
                        SAVE["gold"] += chosen_enemy.get("gold", 0)
                
                # boowomp
                for enemy in enemies_to_remove:
                    enemies.remove(enemy)
            else:
                # normal targetting
                while targets_remaining > 0 and len(enemies) > 0:
                    enemy_picker_menu = Menu(
                        *sorted(str(i + 1) for i in range(len(enemies))),
                        title=f"Which enemy will you target? ({targets_remaining}/{chosen_card.get('targets', 1)})",
                        color="bold red",
                        highlight_color="bold white"
                    )
                    chosen_enemy = enemies[int(enemy_picker_menu.ask(screen=False, esc=False))-1]

                    # apply damage
                    chosen_enemy['hp'] -= chosen_card.get("damage", 0)

                    # and effects
                    if len(chosen_card.get("effects", [])) > 0:
                        if not chosen_enemy.get('effects'):
                            chosen_enemy['effects'] = []
                        for effect in chosen_card.get("effects", []):
                            if effect.get('type') == 'HEAL':
                                SAVE['hp'] += 5
                                effect['duration'] -= 1
                                console.print("You healed 5HP!", style="green")
                                if effect['duration'] != 0:
                                    SAVE['effects'].append(effect)
                            elif effect.get('type') == 'CLEANSE':
                                console.print("You cleansed yourself, removing all effects!", style="green")
                                SAVE['effects'] = []
                            elif effect not in chosen_enemy['effects']:
                                chosen_enemy['effects'].append(effect)

                    targets_remaining -= 1

                    # kablamo
                    if chosen_enemy['hp'] <= 0:
                        enemies.remove(chosen_enemy)
                        SAVE["gold"] += chosen_enemy.get("gold", 0)

            # aw man that was a scroll
            if chosen_card.get("scroll", False):
                SAVE["hand"].remove(chosen_card)

            # chopped
            process_enemy_effects(enemies)

            # mega kablamo?
            if len(enemies) == 0:
                console.print("You have defeated all enemies on this floor!", style="bold green")
                SAVE["floor"] += 1
                SAVE["tp"] = SAVE.get("max_tp", 2)
                
                # save game after each floor
                save_game(SAVE_PATH)
                
                # Check for shops
                if SAVE["floor"] % 10 == 0:  # voucher shop every 10 floors
                    voucher_shop()
                    save_game(SAVE_PATH)  # save after shop
                elif SAVE["floor"] % 5 == 0:  # scroll shop every 5 floors (not 10)
                    scroll_shop()
                    save_game(SAVE_PATH)  # save after shop
                
                Prompt.ask("Press Enter to continue...")
                break  # mega kablamo.

while True:
    # console.clear() is finnicky, so try the more robust:
    result = os.system('cls' if os.name == 'nt' else 'clear')
    if result != 0:
        # and if that doesn't work, then we'll use it
        console.clear()

    selection = mainMenu.ask(screen = False, esc = False)
    # Handle the selection
    match selection:
        case "New Run":
            BASE = "new-run"
            NEWRUN = BASE
            save_dir = get_save_directory()
            i = 0
            while (save_dir / f"{NEWRUN}.sbr").exists():
                i += 1
                NEWRUN = f"{BASE}-{i}"
            save_name = Prompt.ask("Enter a name for your run (a-z, A-Z, -, _, 0-9)",
                                   default=NEWRUN)
            if not save_name or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in save_name):
                console.print("Invalid save name!", style="bold red")
                continue
            save_path = save_dir / f"{save_name}.sbr"
            if save_path.exists():
                overwrite = Prompt.ask(f"A save named '{save_name}' already exists. Overwrite? (y/n)",
                                       choices=["y", "n"], default="n")
                if overwrite == "n":
                    continue
            try:
                save_data = copy.deepcopy(TEMPLATESAVE)
                save_data["name"] = save_name
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)
            except OSError as e:
                console.print(f"Failed to create save file: {e}", style="bold red")
                continue
            console.print("Starting new run...", style="italic white")
            entry(str(save_path))
        case "Continue Run":
            save_dir = get_save_directory()
            save_files = [f.stem for f in save_dir.glob("*.sbr")]
            if not save_files:
                console.print("No saved runs found!", style="bold red")
            else:
                loadSaveMenu = Menu(
                    *sorted(save_files),
                    "Back",
                    title="Select a run to continue",
                    color="bold blue",
                    highlight_color="bold white",
                )
                selection = loadSaveMenu.ask(screen = False, esc = False)

                if selection == "Back":
                    continue

                console.print("Starting...", style="italic white")
                entry(str(save_dir / f"{selection}.sbr"))
        case "Exit":
            console.print("Goodbye!", style="italic cyan")
            sys.exit()