from sqlalchemy.orm import Session
import logging
from .db import SessionLocal
from .models import Base, ContentItem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Massively expanded catalog with VERIFIED TMDB poster paths (w500 size)
SEED_ITEMS = [
    # --- HORROR ---
    {"kind": "movie", "title": "Child's Play", "genres": "Horror, Thriller", "keywords": "chucky, doll, possession", "synopsis": "A mother gives her son a toy doll for his birthday, unaware that it is possessed by the soul of a serial killer.", "image_url": "https://image.tmdb.org/t/p/w500/vS7TOn9IeF9FqB7m8D2i8yX6W2e.jpg"},
    {"kind": "movie", "title": "IT", "genres": "Horror, Fantasy", "keywords": "clown, kids, sewer", "synopsis": "A group of bullied kids band together to destroy a shape-shifting monster, which disguises itself as a clown.", "image_url": "https://image.tmdb.org/t/p/w500/9Rj8l6gElLpRL7Kj17iZhrT5Zuw.jpg"},
    {"kind": "movie", "title": "Scream", "genres": "Horror, Mystery", "keywords": "ghostface, slasher", "synopsis": "A year after the murder of her mother, a teenage girl is terrorized by a new killer.", "image_url": "https://image.tmdb.org/t/p/w500/lpdrU99v0uYvS2oKxU30c904Fj6.jpg"},
    {"kind": "movie", "title": "A Nightmare on Elm Street", "genres": "Horror", "keywords": "freddy krueger, dreams", "synopsis": "The spirit of a child murderer seeks revenge by invading the dreams of teenagers.", "image_url": "https://image.tmdb.org/t/p/w500/iS9UORp7fLpW4UToa7I2fFh2U4E.jpg"},
    {"kind": "movie", "title": "The Conjuring", "genres": "Horror, Thriller", "keywords": "paranormal, haunting", "synopsis": "Investigators Ed and Lorraine Warren work to help a family terrorized by a dark presence.", "image_url": "https://image.tmdb.org/t/p/w500/w9MqGv3uD96WFv98GWyYpI9U87z.jpg"},
    {"kind": "movie", "title": "Halloween", "genres": "Horror", "keywords": "michael myers, slasher", "synopsis": "Michael Myers escapes from a mental hospital and returns to kill again.", "image_url": "https://image.tmdb.org/t/p/w500/wijlZ3HaYMvlDTPqJoTCWKFkCPU.jpg"},
    {"kind": "movie", "title": "Hereditary", "genres": "Horror, Mystery", "keywords": "family, trauma, cult", "synopsis": "After the matriarch of the Graham family passes away, her daughter and grandchildren are haunted by disturbing occurrences.", "image_url": "https://image.tmdb.org/t/p/w500/mwVli0W57n5Uq2E283TjE2.jpg"},
    {"kind": "movie", "title": "Midsommar", "genres": "Horror, Drama", "keywords": "cult, sweden, sun", "synopsis": "A couple travels to Scandinavia to visit a rural hometown's fabled Swedish midsummer festival.", "image_url": "https://image.tmdb.org/t/p/w500/7Ure2B8Q6p6J5E8eO9L2n8N7L0S.jpg"},
    {"kind": "movie", "title": "The Babadook", "genres": "Horror, Thriller", "keywords": "book, grief, monster", "synopsis": "A single mother battles with her son's fear of a monster.", "image_url": "https://image.tmdb.org/t/p/w500/onX18Xy0UoYV0W9D079XUuV8fD.jpg"},
    {"kind": "movie", "title": "Psycho", "genres": "Horror, Thriller", "keywords": "hitchcock, motel", "synopsis": "A secretary checks into a remote motel run by a young man under the domination of his mother.", "image_url": "https://image.tmdb.org/t/p/w500/81d8oyEFgj7FlxJqSDXWr8JH8kV.jpg"},
    {"kind": "movie", "title": "Saw", "genres": "Horror, Thriller", "keywords": "jigsaw, trap", "synopsis": "Two strangers awaken in a room and discover they're pawns in a deadly game.", "image_url": "https://image.tmdb.org/t/p/w500/vY8L456qObeidOaS4Z9pZPrhVlG.jpg"},
    {"kind": "movie", "title": "The Exorcist", "genres": "Horror", "keywords": "possession, demon", "synopsis": "When a young girl is possessed by a mysterious entity, her mother seeks the help of two priests.", "image_url": "https://image.tmdb.org/t/p/w500/7vHofP6pP2jshGkO733989Mv5Hn.jpg"},
    {"kind": "movie", "title": "The Shining", "genres": "Horror", "keywords": "hotel, isolation, madness", "synopsis": "A family heads to an isolated hotel for the winter where an evil presence influences the father into violence.", "image_url": "https://image.tmdb.org/t/p/w500/x9q7fb6Y6X7TOC978S669m5asUf.jpg"},
    {"kind": "movie", "title": "The Texas Chain Saw Massacre", "genres": "Horror", "keywords": "leatherface, chainsaw", "synopsis": "Friends visiting their grandfather's house are hunted by a chain-saw wielding killer.", "image_url": "https://image.tmdb.org/t/p/w500/a39S8pDeu0vY98ol89vREz9vS3W.jpg"},
    {"kind": "movie", "title": "Alien", "genres": "Horror, Sci-Fi", "keywords": "space, monster", "synopsis": "The crew of a spacecraft encounters a deadly lifeform after investigating an unknown transmission.", "image_url": "https://image.tmdb.org/t/p/w500/vfrQk5IPloGg1v9Rzbh2Eg3VGyM.jpg"},

    # --- THRILLER ---
    {"kind": "movie", "title": "Se7en", "genres": "Crime, Thriller", "keywords": "serial killer, sins", "synopsis": "Two detectives hunt a serial killer who uses the seven deadly sins as his motives.", "image_url": "https://image.tmdb.org/t/p/w500/191nKfP0ehp3uIvWqgPbFmI4lv9.jpg"},
    {"kind": "movie", "title": "The Silence of the Lambs", "genres": "Thriller, Crime", "keywords": "hannibal lecter, fbi", "synopsis": "A young F.B.I. cadet must receive the help of an incarcerated cannibal killer.", "image_url": "https://image.tmdb.org/t/p/w500/rXBSOoeSExJ4Yy9184P5L7oY845.jpg"},
    {"kind": "movie", "title": "Inception", "genres": "Sci-Fi, Thriller", "keywords": "dreams, heist", "synopsis": "A thief who steals secrets through dream-sharing must perform inception.", "image_url": "https://image.tmdb.org/t/p/w500/9gk7Fn9sVAsS9Te6u19uPB0UuRn.jpg"},
    {"kind": "movie", "title": "Joker", "genres": "Crime, Thriller, Drama", "keywords": "madness, clown, origin", "synopsis": "A failed stand-up comedian is driven insane and turns to a life of crime and chaos.", "image_url": "https://image.tmdb.org/t/p/w500/udDclKVXv9qZfwWgqwsREWgR0Y6.jpg"},
    {"kind": "movie", "title": "Parasite", "genres": "Thriller, Drama", "keywords": "class, family, deception", "synopsis": "Greed and class discrimination threaten a newly formed relationship between two families.", "image_url": "https://image.tmdb.org/t/p/w500/7IiTTjMvIS7_Z7u6pBv9S9et9Um.jpg"},
    {"kind": "movie", "title": "Shutter Island", "genres": "Thriller, Mystery", "keywords": "island, mental, twists", "synopsis": "A U.S. Marshal investigates the disappearance of a murderer who escaped from a hospital.", "image_url": "https://image.tmdb.org/t/p/w500/kve20sXvUZS1pS4u6h6vT6oR0Z3.jpg"},
    {"kind": "movie", "title": "Gone Girl", "genres": "Thriller, Mystery", "keywords": "missing, marriage, media", "synopsis": "A man becomes the focus of an intense media circus after his wife's disappearance.", "image_url": "https://image.tmdb.org/t/p/w500/qymaMbiB7651BYDndvUzwC67z56.jpg"},
    {"kind": "movie", "title": "Memento", "genres": "Thriller, Mystery", "keywords": "memory, revenge", "synopsis": "A man with short-term memory loss attempts to track down his wife's murderer.", "image_url": "https://image.tmdb.org/t/p/w500/fKTPH2WvH8nHTXeBYBVhawtRqtR.jpg"},
    {"kind": "movie", "title": "Oldboy", "genres": "Thriller, Action", "keywords": "revenge, mystery", "synopsis": "After being kidnapped and imprisoned for fifteen years, a man is released and must find his captor.", "image_url": "https://image.tmdb.org/t/p/w500/649SbiuCHZhpv9pL97669YpI5A.jpg"},
    {"kind": "movie", "title": "The Prestige", "genres": "Thriller, Mystery", "keywords": "magic, rivalry, twist", "synopsis": "Two stage magicians in 1890s London engage in a battle to create the ultimate illusion.", "image_url": "https://image.tmdb.org/t/p/w500/bdN3gY6vG6YpP9rV8R1L1X6A9L1.jpg"},

    # --- ACTION / ADVENTURE ---
    {"kind": "movie", "title": "Interstellar", "genres": "Sci-Fi, Adventure", "keywords": "space, time", "synopsis": "A team of explorers travel through a wormhole in search of a new home for humanity.", "image_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6vCU679yvBPu9.jpg"},
    {"kind": "movie", "title": "The Matrix", "genres": "Sci-Fi, Action", "keywords": "reality, simulation", "synopsis": "A hacker learns the truth about his world and his role in the war against its controllers.", "image_url": "https://image.tmdb.org/t/p/w500/f89U3Y9S7qwbk05pS78qnYvX1zE.jpg"},
    {"kind": "movie", "title": "The Dark Knight", "genres": "Action, Crime", "keywords": "batman, joker", "synopsis": "Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.", "image_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDp9sS1hfzh9Rql9S0n.jpg"},
    {"kind": "movie", "title": "Avengers: Endgame", "genres": "Action, Sci-Fi", "keywords": "superhero, marvel", "synopsis": "The Avengers assemble once more in order to restore order to the universe.", "image_url": "https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg"},
    {"kind": "movie", "title": "Spider-Man: Across the Spider-Verse", "genres": "Action, Animation", "keywords": "multiverse, superhero", "synopsis": "Miles Morales catapults across the Multiverse, where he encounters a team of Spider-People.", "image_url": "https://image.tmdb.org/t/p/w500/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg"},
    {"kind": "movie", "title": "Dune", "genres": "Sci-Fi, Adventure", "keywords": "desert, prophecy, space", "synopsis": "Paul Atreides must travel to the most dangerous planet in the universe to ensure the future of his people.", "image_url": "https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg"},
    {"kind": "movie", "title": "Top Gun: Maverick", "genres": "Action, Drama", "keywords": "flying, jet, pilot", "synopsis": "Pete Mitchell is where he belongs, pushing the envelope as a courageous test pilot.", "image_url": "https://image.tmdb.org/t/p/w500/jMLiTgCo0vXJuwMzZGoNOUPfuj7.jpg"},
    {"kind": "movie", "title": "Mad Max: Fury Road", "genres": "Action, Sci-Fi", "keywords": "post-apocalyptic, chase", "synopsis": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler.", "image_url": "https://image.tmdb.org/t/p/w500/kqjL17yufvn9OVLyXYpvtyrFfak.jpg"},
    {"kind": "movie", "title": "John Wick", "genres": "Action, Thriller", "keywords": "assassin, dog, revenge", "synopsis": "An ex-hit-man comes out of retirement to track down the gangsters that took everything from him.", "image_url": "https://image.tmdb.org/t/p/w500/5vHssUeVe25bMrof1HyaPyWgaP.jpg"},
    {"kind": "movie", "title": "Gladiator", "genres": "Action, Drama", "keywords": "rome, revenge", "synopsis": "A former Roman General sets out to exact vengeance against the corrupt emperor.", "image_url": "https://image.tmdb.org/t/p/w500/ty8TGRvS4vMvREXoGP1o9SzwWyR.jpg"},
    {"kind": "movie", "title": "Blade Runner 2049", "genres": "Sci-Fi, Drama", "keywords": "replicant, memory, visual", "synopsis": "A young blade runner's discovery of a long-buried secret leads him to track down Rick Deckard.", "image_url": "https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg"},

    # --- DRAMA / CRIME / CLASSICS ---
    {"kind": "movie", "title": "The Godfather", "genres": "Crime, Drama", "keywords": "mafia, family", "synopsis": "The aging patriarch of an organized crime dynasty transfers control to his reluctant son.", "image_url": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg"},
    {"kind": "movie", "title": "Pulp Fiction", "genres": "Crime, Drama", "keywords": "hitman, boxing, drugs", "synopsis": "The lives of two mob hitmen, a boxer, and a gangster's wife intertwine in four tales of violence.", "image_url": "https://image.tmdb.org/t/p/w500/d5iIl9h9F9pS3snUsPSbs9VzARi.jpg"},
    {"kind": "movie", "title": "The Shawshank Redemption", "genres": "Drama", "keywords": "prison, hope", "synopsis": "Two imprisoned men bond over a number of years, finding solace and eventual redemption.", "image_url": "https://image.tmdb.org/t/p/w500/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg"},
    {"kind": "movie", "title": "Fight Club", "genres": "Drama", "keywords": "insomnia, soap", "synopsis": "An insomniac office worker and a devil-may-care soap maker form an underground fight club.", "image_url": "https://image.tmdb.org/t/p/w500/pB8BM7pdv9ovvyhNn07vI7dyvXn.jpg"},
    {"kind": "movie", "title": "Forrest Gump", "genres": "Drama, Romance", "keywords": "history, life", "synopsis": "The presidencies of Kennedy and Johnson, and other events unfold from the perspective of an Alabama man.", "image_url": "https://image.tmdb.org/t/p/w500/arw2vcBveWOVWm63YvSJNp7t0Jp.jpg"},
    {"kind": "movie", "title": "GoodFellas", "genres": "Crime, Drama", "keywords": "mafia, true story", "synopsis": "The story of Henry Hill and his life in the mob.", "image_url": "https://image.tmdb.org/t/p/w500/aKuFiU8tVZ5Sbtv7kf8N30p6zpB.jpg"},
    {"kind": "movie", "title": "Schindler's List", "genres": "Drama, History", "keywords": "holocaust, hero", "synopsis": "Industrialist Oskar Schindler gradually becomes concerned for his Jewish workforce.", "image_url": "https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg"},

    # --- SERIES / ANIME ---
    {"kind": "series", "title": "Stranger Things", "genres": "Sci-Fi, Horror", "keywords": "kids, 80s", "synopsis": "In 1980s Indiana, a series of supernatural events forces a group of kids to unravel mysteries.", "image_url": "https://image.tmdb.org/t/p/w500/49WfT1UuUpWShwinv29qCbuO8zs.jpg"},
    {"kind": "series", "title": "Breaking Bad", "genres": "Crime, Drama", "keywords": "meth, drug", "synopsis": "A chemistry teacher turned meth maker navigates the consequences of his double life.", "image_url": "https://image.tmdb.org/t/p/w500/ggGT0e6Ls2X4HGh9P1u019B1rAs.jpg"},
    {"kind": "series", "title": "The Last of Us", "genres": "Drama, Sci-Fi", "keywords": "zombie, survival", "synopsis": "Joel is hired to smuggle Ellie out of an oppressive quarantine zone.", "image_url": "https://image.tmdb.org/t/p/w500/p0AtD0ivSlHq2MHY6JFgyhNqAQY.jpg"},
    {"kind": "series", "title": "Game of Thrones", "genres": "Fantasy, Drama", "keywords": "throne, dragons", "synopsis": "Noble families fight for control over the lands of Westeros.", "image_url": "https://image.tmdb.org/t/p/w500/7WUHnWGx5OO145IRxPDUkQSh4C7.jpg"},
    {"kind": "series", "title": "Better Call Saul", "genres": "Crime, Drama", "keywords": "lawyer, prequel", "synopsis": "The trials and tribulations of criminal lawyer Jimmy McGill.", "image_url": "https://image.tmdb.org/t/p/w500/fC2S9Fl9SUE6yvAypH606S6SjYf.jpg"},
    {"kind": "series", "title": "The Boys", "genres": "Action, Sci-Fi", "keywords": "superhero, dark", "synopsis": "A group of vigilantes set out to take down corrupt superheroes.", "image_url": "https://image.tmdb.org/t/p/w500/7Ns998u6hYUnU04pU6YpUvw9vS.jpg"},
    {"kind": "anime", "title": "Attack on Titan", "genres": "Action, Drama", "keywords": "titans, survival", "synopsis": "Humanity fights for survival against gigantic titans.", "image_url": "https://image.tmdb.org/t/p/w500/h9z79HL9YgYwiWVpAd8631pMpM2.jpg"},
    {"kind": "anime", "title": "Demon Slayer: Kimetsu no Yaiba", "genres": "Action, Fantasy", "keywords": "demons, swords", "synopsis": "A boy becomes a demon slayer after his family is attacked by demons.", "image_url": "https://image.tmdb.org/t/p/w500/h888UlsD9E7Y7iYp1D8qR3Y2A0Z.jpg"},
    {"kind": "anime", "title": "One Piece", "genres": "Action, Adventure", "keywords": "pirate, rubber", "synopsis": "Luffy sets off on a journey to find the titular treasure.", "image_url": "https://image.tmdb.org/t/p/w500/fcXdJlbSdUEeMSJFsXKsznGwwok.jpg"},
    {"kind": "anime", "title": "Jujutsu Kaisen", "genres": "Action, Fantasy", "keywords": "curses, magic", "synopsis": "A boy swallows a cursed talisman and finds himself becoming the host of a powerful Curse.", "image_url": "https://image.tmdb.org/t/p/w500/aI1fm7H2rhfRxnwWIdVACR3k1fO.jpg"},
    {"kind": "anime", "title": "Death Note", "genres": "Mystery, Thriller", "keywords": "notebook, shinigami", "synopsis": "An intelligent student discovers a notebook capable of killing anyone.", "image_url": "https://image.tmdb.org/t/p/w500/o7pZEzOKDGalpH5fTWZnVO9yKLV.jpg"},
    {"kind": "anime", "title": "Naruto Shippuden", "genres": "Action, Adventure", "keywords": "ninja, fox", "synopsis": "Naruto Uzumaki searches for recognition and aims to become the Hokage.", "image_url": "https://image.tmdb.org/t/p/w500/zP5SftyPx2VCdly369kTVVNIcT3.jpg"},
    {"kind": "anime", "title": "Fullmetal Alchemist: Brotherhood", "genres": "Action, Adventure", "keywords": "alchemy, brothers", "synopsis": "Two brothers search for a way to restore their bodies.", "image_url": "https://image.tmdb.org/t/p/w500/A6tMQAo6t6eRFCPhsrShmxZLqFB.jpg"}
]

def main():
    db: Session = SessionLocal()
    try:
        logger.info("Creating missing tables...")
        Base.metadata.create_all(bind=db.get_bind())

        logger.info(f"Seeding {len(SEED_ITEMS)} catalog items without deleting existing posters...")
        for it in SEED_ITEMS:
            existing = (
                db.query(ContentItem)
                .filter(ContentItem.title == it["title"], ContentItem.kind == it["kind"])
                .one_or_none()
            )

            if existing:
                existing.genres = it["genres"]
                existing.keywords = it["keywords"]
                existing.synopsis = it["synopsis"]
                if not existing.image_url:
                    existing.image_url = it["image_url"]
                continue

            db.add(
                ContentItem(
                    kind=it["kind"],
                    title=it["title"],
                    genres=it["genres"],
                    keywords=it["keywords"],
                    synopsis=it["synopsis"],
                    image_url=it["image_url"],
                )
            )
        db.commit()
        logger.info("Database seeding completed successfully.")
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
