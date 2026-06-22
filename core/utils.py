import random
import string

def generate_matricule(prefix="ETU"):
    return prefix + ''.join(random.choices(string.digits, k=6))