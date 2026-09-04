blocked_domains = []

with open("blocklist.txt", "r") as file:

    for line in file:

        domain = line.strip().lower()

        blocked_domains.append(domain)

domain = input("Enter domain: ").strip().lower()

blocked = False

for blocked_domain in blocked_domains:

    if domain == blocked_domain:
        blocked = True
        break

    if domain.endswith("." + blocked_domain):
        blocked = True
        break


if blocked:
    print("BLOCKED")
else:
    print("ALLOWED")