from utils.users_store import load_users, save_users


def add_tokens(username: str, amount: int) -> int | None:
    users = load_users()
    if username not in users:
        return None
    users[username]["tokens"] = users[username].get("tokens", 0) + amount
    new_balance = users[username]["tokens"]
    save_users(users)
    return new_balance


def unlock_with_cost(username: str, unlock_id: str, cost: int = 1) -> tuple[bool, int]:
    users = load_users()
    if username not in users:
        return False, 0

    user = users[username]
    user.setdefault("unlocked", [])
    balance = user.get("tokens", 0)

    if unlock_id in user["unlocked"]:
        return True, balance
    if balance < cost:
        return False, balance

    user["tokens"] = balance - cost
    user["unlocked"].append(unlock_id)
    new_balance = user["tokens"]
    save_users(users)
    return True, new_balance
