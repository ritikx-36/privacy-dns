blocked_domains = []

with open("blocklist.txt", "r") as file:
    for line in file:
        domain = line.strip()
        blocked_domains.append(domain)

domain = input("Enter domain: ")

if domain in blocked_domains:
    print("BLOCKED")
else:
    print("ALLOWED")
