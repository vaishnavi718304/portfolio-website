def print_header(title: str):
    bar = "=" * max(18, len(title))
    print(f"\n{bar}\n{title}\n{bar}")

def ask(prompt: str) -> str:
    return input(f"{prompt}: ").strip()

def pause():
    input("\nPress Enter to continue...")
