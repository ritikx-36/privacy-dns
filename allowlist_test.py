blocked_domains = []
allowed_domains = []


# Load blocklist
with open("blocklist.txt", "r") as file:
    for line in file:
        domain = line.strip().lower()

        if domain:
            blocked_domains.append(domain)


# Load allowlist
with open("allowlist.txt", "r") as file:
    for line in file:
        domain = line.strip().lower()

        if domain:
            allowed_domains.append(domain)


domain = input("Enter domain: ").strip().lower()


# Check allowlist first
allowed = False

for allowed_domain in allowed_domains:

    if domain == allowed_domain:
        allowed = True
        break

    if domain.endswith("." + allowed_domain):
        allowed = True
        break


if allowed:
    print("ALLOWED")
else:

    # Check blocklist
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
