# Setup unit tests

sudo -u $USER psql postgres

Run the following SQL commands to create the test databases and tables:

```
CREATE ROLE waii WITH LOGIN CREATEDB PASSWORD 'password';
```

Create DB1

```
CREATE DATABASE waii_sdk_test;
\c waii_sdk_test;
CREATE table public.movies (id serial primary key, title text, year integer, runtime integer, genres text[], director text, actors text[], plot text, poster text, imdb text, production text, website text, response text, created_at timestamp, updated_at timestamp);
INSERT INTO public.movies (title, year, runtime, genres, director, actors, plot, poster, imdb, production, website, response, created_at, updated_at)
VALUES
    ('The Shawshank Redemption', 1994, 142, ARRAY['Drama'], 'Frank Darabont', ARRAY['Tim Robbins', 'Morgan Freeman', 'Bob Gunton'], 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.', 'http://example.com/shawshank.jpg', 'tt0111161', 'Castle Rock Entertainment', 'http://www.shawshankredemption.com', 'True', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    ('Inception', 2010, 148, ARRAY['Action', 'Adventure', 'Sci-Fi'], 'Christopher Nolan', ARRAY['Leonardo DiCaprio', 'Joseph Gordon-Levitt', 'Ellen Page'], 'A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.', 'http://example.com/inception.jpg', 'tt1375666', 'Warner Bros. Pictures', 'http://www.inception-movie.com', 'True', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    ('Pulp Fiction', 1994, 154, ARRAY['Crime', 'Drama'], 'Quentin Tarantino', ARRAY['John Travolta', 'Uma Thurman', 'Samuel L. Jackson'], 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.', 'http://example.com/pulpfiction.jpg', 'tt0110912', 'Miramax', 'http://www.pulpfiction.com', 'True', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    ('The Matrix', 1999, 136, ARRAY['Action', 'Sci-Fi'], 'Lana Wachowski, Lilly Wachowski', ARRAY['Keanu Reeves', 'Laurence Fishburne', 'Carrie-Anne Moss'], 'A computer programmer discovers that reality as he knows it is a simulation created by machines to subjugate humanity.', 'http://example.com/matrix.jpg', 'tt0133093', 'Warner Bros. Pictures', 'http://www.whatisthematrix.com', 'True', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
    
GRANT ALL PRIVILEGES ON DATABASE waii_sdk_test TO waii;
GRANT ALL PRIVILEGES ON TABLE public.movies TO waii;

CREATE DATABASE waii_sdk_test_copy;
\c waii_sdk_test_copy;
CREATE table public.movies (id serial primary key, title text, year integer, runtime integer, genres text[], director text, actors text[], plot text, poster text, imdb text, production text, website text, response text, created_at timestamp, updated_at timestamp);
INSERT INTO public.movies (title, year, runtime, genres, director, actors, plot, poster, imdb, production, website, response, created_at, updated_at)
VALUES
    ('The Shawshank Redemption', 1994, 142, ARRAY['Drama'], 'Frank Darabont', ARRAY['Tim Robbins', 'Morgan Freeman', 'Bob Gunton'], 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.', 'http://example.com/shawshank.jpg', 'tt0111161', 'Castle Rock Entertainment', 'http://www.shawshankredemption.com', 'True', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    ('Inception', 2010, 148, ARRAY['Action', 'Adventure', 'Sci-Fi'], 'Christopher Nolan', ARRAY['Leonardo DiCaprio', 'Joseph Gordon-Levitt', 'Ellen Page'], 'A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.', 'http://example.com/inception.jpg', 'tt1375666', 'Warner Bros. Pictures', 'http://www.inception-movie.com', 'True', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    ('Pulp Fiction', 1994, 154, ARRAY['Crime', 'Drama'], 'Quentin Tarantino', ARRAY['John Travolta', 'Uma Thurman', 'Samuel L. Jackson'], 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.', 'http://example.com/pulpfiction.jpg', 'tt0110912', 'Miramax', 'http://www.pulpfiction.com', 'True', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    ('The Matrix', 1999, 136, ARRAY['Action', 'Sci-Fi'], 'Lana Wachowski, Lilly Wachowski', ARRAY['Keanu Reeves', 'Laurence Fishburne', 'Carrie-Anne Moss'], 'A computer programmer discovers that reality as he knows it is a simulation created by machines to subjugate humanity.', 'http://example.com/matrix.jpg', 'tt0133093', 'Warner Bros. Pictures', 'http://www.whatisthematrix.com', 'True', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
    
GRANT ALL PRIVILEGES ON DATABASE waii_sdk_test_copy TO waii;
GRANT ALL PRIVILEGES ON TABLE public.movies TO waii;

CREATE DATABASE waii_sdk_test2;
\c waii_sdk_test2;
CREATE table public.albums (id serial primary key, title text, year integer, artist text, genre text, tracks text[], cover text, website text, created_at timestamp, updated_at timestamp);

INSERT INTO public.albums (title, year, artist, genre, tracks, cover, website, created_at, updated_at)
VALUES
    ('Thriller', 1982, 'Michael Jackson', 'Pop', 
    ARRAY['Wanna Be Startin'' Somethin''', 'Baby Be Mine', 'The Girl Is Mine', 'Thriller', 'Beat It', 'Billie Jean', 'Human Nature', 'P.Y.T. (Pretty Young Thing)', 'The Lady in My Life'],
    'http://example.com/thriller.jpg', 'http://www.michaeljackson.com', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    ('Back in Black', 1980, 'AC/DC', 'Hard Rock', 
    ARRAY['Hells Bells', 'Shoot to Thrill', 'What Do You Do for Money Honey', 'Given the Dog a Bone', 'Let Me Put My Love Into You', 'Back in Black', 'You Shook Me All Night Long', 'Have a Drink on Me', 'Shake a Leg', 'Rock and Roll Ain''t Noise Pollution'],
    'http://example.com/backinblack.jpg', 'http://www.acdc.com', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    ('21', 2011, 'Adele', 'Pop', 
    ARRAY['Rolling in the Deep', 'Rumour Has It', 'Turning Tables', 'Don''t You Remember', 'Set Fire to the Rain', 'He Won''t Go', 'Take It All', 'I''ll Be Waiting', 'One and Only', 'Lovesong', 'Someone Like You'],
    'http://example.com/21.jpg', 'http://www.adele.com', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    ('The Dark Side of the Moon', 1973, 'Pink Floyd', 'Progressive Rock', 
    ARRAY['Speak to Me', 'Breathe', 'On the Run', 'Time', 'The Great Gig in the Sky', 'Money', 'Us and Them', 'Any Colour You Like', 'Brain Damage', 'Eclipse'],
    'http://example.com/darksideofthemoon.jpg', 'http://www.pinkfloyd.com', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    ('Nevermind', 1991, 'Nirvana', 'Grunge', 
    ARRAY['Smells Like Teen Spirit', 'In Bloom', 'Come as You Are', 'Breed', 'Lithium', 'Polly', 'Territorial Pissings', 'Drain You', 'Lounge Act', 'Stay Away', 'On a Plain', 'Something in the Way'],
    'http://example.com/nevermind.jpg', 'http://www.nirvana.com', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

GRANT ALL PRIVILEGES ON DATABASE waii_sdk_test2 TO waii;
GRANT ALL PRIVILEGES ON TABLE public.albums TO waii;
```

Also ensure you have DB connection to the example snowflake DB - MOVIE_DB. If you do not have this DB connection, consult with a Waii team member for info on this DB connection
