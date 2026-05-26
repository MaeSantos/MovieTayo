import argparse

from sqlalchemy.orm import Session

from .db import SessionLocal
from .models import ContentItem
from .populate_posters import candidate_urls, ensure_column, fetch_data_url


MORE_ITEMS = [
    {
        "kind": "movie",
        "title": "Avatar",
        "genres": "Sci-Fi, Adventure, Fantasy",
        "keywords": "pandora, alien world, marine, ecology",
        "synopsis": "A paraplegic marine becomes part of an alien world and must choose between duty and a new home.",
    },
    {
        "kind": "movie",
        "title": "Avengers: Endgame",
        "genres": "Action, Adventure, Sci-Fi",
        "keywords": "superheroes, time travel, sacrifice, marvel",
        "synopsis": "The Avengers assemble for one final attempt to undo a cosmic disaster.",
    },
    {
        "kind": "movie",
        "title": "Titanic",
        "genres": "Romance, Drama",
        "keywords": "ship, disaster, love, class",
        "synopsis": "A young aristocrat and a free-spirited artist fall in love aboard the doomed ocean liner.",
    },
    {
        "kind": "movie",
        "title": "Joker",
        "genres": "Crime, Drama, Thriller",
        "keywords": "clown, society, descent, gotham",
        "synopsis": "An isolated man in Gotham spirals into violence and transforms into a notorious figure.",
    },
    {
        "kind": "movie",
        "title": "Parasite",
        "genres": "Thriller, Drama, Dark Comedy",
        "keywords": "class, family, deception, wealth",
        "synopsis": "A struggling family infiltrates a wealthy household with consequences that turn explosive.",
    },
    {
        "kind": "anime",
        "title": "Spirited Away",
        "genres": "Fantasy, Adventure, Anime",
        "keywords": "spirits, bathhouse, courage, transformation",
        "synopsis": "A young girl enters a magical spirit world and must find the courage to save her parents.",
    },
    {
        "kind": "anime",
        "title": "Your Name.",
        "genres": "Romance, Fantasy, Anime",
        "keywords": "body swap, fate, comet, memory",
        "synopsis": "Two teenagers mysteriously swap bodies and discover a connection that crosses time and place.",
    },
    {
        "kind": "movie",
        "title": "Toy Story",
        "genres": "Animation, Adventure, Comedy",
        "keywords": "toys, friendship, jealousy, childhood",
        "synopsis": "A cowboy doll feels threatened when a flashy space ranger becomes his owner's new favorite toy.",
    },
    {
        "kind": "movie",
        "title": "Finding Nemo",
        "genres": "Animation, Adventure, Family",
        "keywords": "ocean, fish, father, rescue",
        "synopsis": "A timid clownfish crosses the ocean to rescue his missing son.",
    },
    {
        "kind": "movie",
        "title": "The Lion King",
        "genres": "Animation, Adventure, Drama",
        "keywords": "kingdom, family, exile, destiny",
        "synopsis": "A young lion prince must reclaim his kingdom after tragedy forces him into exile.",
    },
    {
        "kind": "movie",
        "title": "Gladiator",
        "genres": "Action, Drama, Historical",
        "keywords": "rome, revenge, arena, honor",
        "synopsis": "A betrayed Roman general rises as a gladiator to seek justice against a corrupt emperor.",
    },
    {
        "kind": "movie",
        "title": "Fight Club",
        "genres": "Drama, Thriller",
        "keywords": "identity, rebellion, masculinity, chaos",
        "synopsis": "An insomniac office worker forms an underground fight club that grows into something dangerous.",
    },
    {
        "kind": "movie",
        "title": "Forrest Gump",
        "genres": "Drama, Romance",
        "keywords": "life story, history, love, perseverance",
        "synopsis": "A kindhearted man witnesses decades of American history while holding onto lifelong love.",
    },
    {
        "kind": "movie",
        "title": "The Shawshank Redemption",
        "genres": "Drama",
        "keywords": "prison, hope, friendship, escape",
        "synopsis": "Two imprisoned men form a bond through years of hardship and quiet resilience.",
    },
    {
        "kind": "movie",
        "title": "The Godfather",
        "genres": "Crime, Drama",
        "keywords": "mafia, family, power, loyalty",
        "synopsis": "The aging patriarch of a crime family transfers control to his reluctant son.",
    },
    {
        "kind": "movie",
        "title": "Goodfellas",
        "genres": "Crime, Drama",
        "keywords": "gangsters, ambition, betrayal, rise and fall",
        "synopsis": "A young man rises through the mob and faces the brutal cost of life in organized crime.",
    },
    {
        "kind": "movie",
        "title": "Dune: Part Two",
        "genres": "Sci-Fi, Adventure, Drama",
        "keywords": "desert, prophecy, rebellion, spice",
        "synopsis": "Paul Atreides joins the Fremen and faces the burden of revenge, power, and destiny.",
    },
    {
        "kind": "movie",
        "title": "Oppenheimer",
        "genres": "Drama, Biography, Historical",
        "keywords": "atomic bomb, scientist, war, morality",
        "synopsis": "J. Robert Oppenheimer leads the Manhattan Project and confronts the consequences of his creation.",
    },
    {
        "kind": "movie",
        "title": "Barbie",
        "genres": "Comedy, Fantasy, Adventure",
        "keywords": "identity, doll, real world, satire",
        "synopsis": "Barbie leaves her perfect world and discovers complicated truths about identity and humanity.",
    },
    {
        "kind": "movie",
        "title": "Spider-Man: Into the Spider-Verse",
        "genres": "Animation, Action, Adventure",
        "keywords": "spider-man, multiverse, hero, coming of age",
        "synopsis": "Miles Morales becomes Spider-Man and teams up with heroes from across the multiverse.",
    },
    {
        "kind": "movie",
        "title": "Black Panther",
        "genres": "Action, Adventure, Sci-Fi",
        "keywords": "wakanda, king, legacy, superhero",
        "synopsis": "A new king of Wakanda faces a challenger whose vision threatens the nation's future.",
    },
    {
        "kind": "movie",
        "title": "Mad Max: Fury Road",
        "genres": "Action, Adventure, Sci-Fi",
        "keywords": "wasteland, chase, survival, rebellion",
        "synopsis": "In a desert wasteland, two rebels flee a tyrant in a relentless high-speed chase.",
    },
    {
        "kind": "movie",
        "title": "La La Land",
        "genres": "Musical, Romance, Drama",
        "keywords": "music, dreams, hollywood, love",
        "synopsis": "An aspiring actress and a jazz musician fall in love while pursuing their dreams in Los Angeles.",
    },
    {
        "kind": "movie",
        "title": "Whiplash",
        "genres": "Drama, Music",
        "keywords": "drumming, ambition, teacher, obsession",
        "synopsis": "A young drummer's pursuit of greatness collides with an abusive instructor's brutal methods.",
    },
    {
        "kind": "movie",
        "title": "Coco",
        "genres": "Animation, Family, Fantasy",
        "keywords": "music, family, ancestors, memory",
        "synopsis": "A boy journeys through the Land of the Dead to uncover the truth about his family.",
    },
    {
        "kind": "movie",
        "title": "Inside Out",
        "genres": "Animation, Family, Comedy",
        "keywords": "emotions, childhood, memory, growing up",
        "synopsis": "The emotions inside a young girl's mind help her navigate a major life change.",
    },
    {
        "kind": "movie",
        "title": "The Social Network",
        "genres": "Drama, Biography",
        "keywords": "facebook, ambition, betrayal, startup",
        "synopsis": "The creation of Facebook sparks lawsuits, rivalry, and a portrait of ambition in the digital age.",
    },
    {
        "kind": "movie",
        "title": "Everything Everywhere All at Once",
        "genres": "Sci-Fi, Comedy, Adventure",
        "keywords": "multiverse, family, identity, absurd",
        "synopsis": "A laundromat owner is pulled into a multiverse crisis while trying to repair her family.",
    },
    {
        "kind": "movie",
        "title": "John Wick",
        "genres": "Action, Thriller",
        "keywords": "assassin, revenge, underworld, combat",
        "synopsis": "A retired assassin returns to the criminal underworld after a personal loss.",
    },
    {
        "kind": "movie",
        "title": "Knives Out",
        "genres": "Mystery, Comedy, Crime",
        "keywords": "detective, family, murder, inheritance",
        "synopsis": "A detective investigates a wealthy author's death in a household full of secrets.",
    },
]


def store_poster(item: ContentItem):
    for url in candidate_urls(item):
        try:
            print(f"Downloading poster: {item.title} <- {url}")
            item.image_url = url
            item.poster_data_url = fetch_data_url(url)
            return
        except Exception as exc:
            print(f"Failed: {item.title} <- {url} ({exc})")


def main():
    parser = argparse.ArgumentParser(description="Add extra local titles to the catalog.")
    parser.add_argument(
        "--skip-posters",
        action="store_true",
        help="Add titles without trying to download poster data.",
    )
    args = parser.parse_args()

    ensure_column()

    db: Session = SessionLocal()
    try:
        existing_titles = {
            title
            for (title,) in db.query(ContentItem.title).all()
        }

        added = 0
        for data in MORE_ITEMS:
            if data["title"] in existing_titles:
                print(f"Already exists: {data['title']}")
                continue

            item = ContentItem(**data)
            db.add(item)
            db.flush()
            if not args.skip_posters:
                store_poster(item)
            db.commit()
            added += 1

        print(f"Added {added} catalog items.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
