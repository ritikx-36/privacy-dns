def load_domains(filename):

    domains = set()

    with open(filename, "r") as file:

        for line in file:

            domain = line.strip().lower()

            if domain and not domain.startswith("#"):
                domains.add(domain)

    return domains


def matches(domain, rules):

    if domain in rules:
        return True

    for rule in rules:

        if domain.endswith("." + rule):
            return True

    return False


def check_domain(domain, allowed_domains, blocked_domains):

    if matches(domain, allowed_domains):
        return "ALLOW"

    if matches(domain, blocked_domains):
        return "BLOCK"

    return "ALLOW"