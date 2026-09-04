import dns.message
import dns.query

query = dns.message.make_query("google.com", "A")

response = dns.query.udp(query, "1.1.1.1")

print(response)
