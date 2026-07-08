
profile_list = [
            {
                "name": "John Doe",
                "watches_post": ["cat_videos", "documentaries", "sports", "news"]
            },
            {
                "name": "Jane Smith",
                "watches_post": ["cooking", "travel", "music", "comedy"]
            },
            {
                "name": "Alice Johnson",
                "watches_post": ["fashion", "beauty", "lifestyle", "fitness"]
            },
            {
                "name": "Bob Brown",
                "watches_post": ["gaming", "technology", "science", "movies"]
            },
            {
                "name": "Charlie Davis",
                "watches_post": ["history", "politics", "education", "art"]
            }
        ]

async def get_profile(name):
    for profile in profile_list:
        if profile["name"] == name:
            return profile
    return None