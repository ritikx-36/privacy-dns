import os


def load_domains(filename):

    domains = set()

    with open(filename, "r") as file:

        for line in file:

            domain = line.strip().lower()

            if domain and not domain.startswith("#"):
                domains.add(domain)

    return domains


def load_filter_directory(directory):

    blocked_domains = set()

    for filename in os.listdir(directory):

        if filename.endswith(".txt"):

            filepath = os.path.join(directory, filename)

            domains = load_domains(filepath)

            blocked_domains.update(domains)

    return blocked_domains


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