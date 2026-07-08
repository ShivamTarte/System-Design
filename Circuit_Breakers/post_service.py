import random

post = ["news", "sports", "entertainment", "technology", "health", "science", "travel", "food"]

async def get_post():
    return random.choice(post)
        
        