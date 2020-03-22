from random import randint
dealer_cards = []
player_cards = []

playing = True

def start():
    while len(player_cards) < 2:
        player_cards.append(randint(1,11))

def hit():
    response = input("Do you want to hit?")
    if response.lower() == 'yes':
        player_cards.append(randint(1,11))
        print("You got ", player_cards)
    if response.lower() == 'no':
        print("You stayed with " ,player_cards)

def dealerHit():
    global playing
    while True:
        if sum(dealer_cards) > 21:
            return "dealer busted " + str(sum(dealer_cards))
            break
        elif sum(dealer_cards) == 21:
            return "dealer has blackjack " + str(sum(dealer_cards))
            break
        elif sum(dealer_cards) < 17:
            dealer_cards.append(randint(1,11))
            print("The dealer has ", dealer_cards)
        print("dealer should be done playing...")


def game():
    start()
    print("You were dealt: " , player_cards)
    if sum(player_cards) == 21:
        print("You have blackjack! ")
        print(player_cards)
    elif sum(player_cards) < 21:
        hit()
        print("Player has ", player_cards)
    elif sum(player_cards) > 21:
        print("You busted ")
        print("Player has ", player_cards)
    print(dealerHit())
game()