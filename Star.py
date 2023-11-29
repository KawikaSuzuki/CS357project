import json


class DFAError(Exception):
    pass


def checkTransitionsCount(nfa_dfa):
    max_transitions = max(
        len([transition for transition in nfa_dfa["transitions"]
            if transition["current_state"] == state])
        for state in nfa_dfa["states"]
    )

    if max_transitions > 2:
        raise DFAError(
            f"Maximum allowed transitions for a state is 2, but found {max_transitions}")


def checkMissingTransitions(nfa_dfa):
    alphabet = set(nfa_dfa["alphabet"])

    for state in nfa_dfa["states"]:
        state_transitions = set(
            transition["input"] for transition in nfa_dfa["transitions"] if transition["current_state"] == state
        )
        missing_transitions = alphabet - state_transitions

        if missing_transitions:
            raise DFAError(
                f"Missing transitions for state {state} and symbols {missing_transitions}")


def getDFAorNFA(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"There was no input file found at {file_path}.")
    except json.JSONDecodeError:
        print(f"There was an error decoding the JSON file {file_path}.")


def findStartState(data):
    return data['start-state']


def findAcceptState(data):
    return data['accept-state']


def addTransitions(nfa_dfa, new_state, input_symbol, next_state):
    existing_transitions = [
        transition for transition in nfa_dfa["transitions"]
        if (
            transition["current_state"] == new_state
            and transition["input"] == input_symbol
            and transition["next_state"] == next_state
        )
    ]

    if existing_transitions:
        print(
            f"Warning: Duplicate transitions found for {new_state}, {input_symbol}, {next_state}")
    else:
        new_transition = {"current_state": new_state,
                          "input": input_symbol, "next_state": next_state}
        nfa_dfa["transitions"].append(new_transition)


def generateStates(nfa_dfa):
    new_nfa_dfa = nfa_dfa.copy()
    new_initial_state = "q0'"
    new_nfa_dfa["states"].append(new_initial_state)
    new_nfa_dfa["accept-state"].append(new_initial_state)
    return new_nfa_dfa, new_initial_state


def applyStar(input_number):
    input_file_path = f"input{input_number}.json"
    data = getDFAorNFA(input_file_path)
    new_nfa_dfa, new_initial_state = generateStates(data)

    addTransitions(new_nfa_dfa, new_initial_state,
                   "epsilon", findStartState(data))

    for accept_state in findAcceptState(data):
        if accept_state != new_initial_state:
            addTransitions(new_nfa_dfa, accept_state,
                           "epsilon", findStartState(data))

    if findStartState(data) in findAcceptState(data):
        new_nfa_dfa["transitions"] = [
            transition for transition in new_nfa_dfa["transitions"] if not (
                transition["current_state"] == findStartState(data)
                and transition["input"] == "epsilon"
                and transition["next_state"] == new_initial_state
            )
        ]

    new_nfa_dfa["start-state"] = new_initial_state

    with open("output.json", 'w') as json_file:
        json.dump(new_nfa_dfa, json_file, indent=2)

    # Check for errors
    try:
        checkTransitionsCount(new_nfa_dfa)
        checkMissingTransitions(new_nfa_dfa)
    except DFAError as e:
        print(e)


if __name__ == "__main__":
    try:
        input_number = int(input("Enter the number of the input file (1-6): "))
        if 1 <= input_number <= 6:
            applyStar(input_number)
        else:
            print("Invalid input number. Please enter a number between 1 and 6.")
    except ValueError:
        print("Invalid input. Please enter a number.")
