BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "bio_history" (
	"bioID"	INTEGER,
	"userID"	INTEGER NOT NULL,
	"old_bio"	TEXT NOT NULL,
	"updated_at"	NUMERIC DEFAULT (strftime('%s', 'now')),
	PRIMARY KEY("bioID" AUTOINCREMENT),
	FOREIGN KEY("userID") REFERENCES "roommate_profiles"("userID")
);
CREATE TABLE IF NOT EXISTS "hobbies" (
	"hobbyID"	,
	"hobby"	TEXT NOT NULL CHECK("hobby" IN ('Sports', 'Music', 'Gaming', 'Cooking', 'Reading', 'Traveling')) UNIQUE,
	PRIMARY KEY("hobbyID")
);
CREATE TABLE IF NOT EXISTS "roommate_profiles" (
	"userID"	INTEGER,
	"firstname"	TEXT NOT NULL,
	"lastname"	TEXT NOT NULL,
	"case_email"	TEXT NOT NULL UNIQUE,
	"gender"	TEXT NOT NULL CHECK("gender" IN ('Male', 'Female', 'Other')),
	"gender_preference"	TEXT NOT NULL CHECK("gender_preference" IN ('Male', 'Female', 'Other', 'No Preference')),
	"housing"	TEXT NOT NULL CHECK("housing" IN ('On-Campus', 'Off-Campus')),
	"year"	TEXT NOT NULL CHECK("year" IN ('Incoming Freshman', 'Incoming Sophomore', 'Incoming Upperclassman')),
	"major"	TEXT NOT NULL CHECK("major" IN ('Engineering', 'Humanities', 'Arts & Sciences', 'Business/Finance')),
	"major_preference"	TEXT NOT NULL CHECK("major_preference" IN ('Engineering', 'Humanities', 'Arts & Sciences', 'Business/Finance', 'No Preference')),
	"clean"	TEXT NOT NULL CHECK("clean" IN ('Very Messy', 'Somewhat Messy', 'Somewhat Clean', 'Very Clean')),
	"noise"	TEXT NOT NULL CHECK("noise" IN ('Very Loud', 'Somewhat Loud', 'Somewhat Quiet', 'Very Quiet')),
	"sleep"	TEXT NOT NULL CHECK("sleep" IN ('Before 10PM', '11PM - 12AM', '12AM - 2AM', '2AM or Later')),
	"greeklife"	TEXT NOT NULL CHECK("greeklife" IN ('Yes', 'No')),
	"guests"	TEXT NOT NULL CHECK("guests" IN ('Never', '1-2 times/week', '3-4 times/week', 'Everyday')),
	"language"	TEXT NOT NULL CHECK("language" IN ('English', 'Chinese', 'Spanish', 'French', 'Hindi', 'Japanese', 'Korean', 'Italian', 'Other')),
	"cook"	TEXT NOT NULL CHECK("cook" IN ('Never', '1-2 times/week', '3-4 times/week', 'Everyday')),
	"smoke"	TEXT NOT NULL CHECK("smoke" IN ('Yes', 'No')),
	"against_smoker"	TEXT NOT NULL CHECK("against_smoker" IN ('Yes', 'No')),
	"drink"	TEXT NOT NULL CHECK("drink" IN ('Yes', 'No')),
	"against_drinker"	TEXT NOT NULL CHECK("against_drinker" IN ('Yes', 'No')),
	"pets"	TEXT NOT NULL CHECK("pets" IN ('Cat', 'Dog', 'Other', 'None')),
	"against_pet"	TEXT NOT NULL CHECK("against_pet" IN ('Yes', 'No')),
	"politics"	TEXT NOT NULL CHECK("politics" IN ('Liberal', 'Moderate', 'Conservative', 'Other')),
	"politics_preference"	TEXT NOT NULL CHECK("politics_preference" IN ('Liberal', 'Moderate', 'Conservative', 'Other', 'No Preference')),
	"religion"	TEXT NOT NULL CHECK("religion" IN ('Christianity', 'Islam', 'Judaism', 'Hinduism', 'Buddhism', 'Sikhism', 'Atheism/Agnosticism', 'Other')),
	"religion_preference"	TEXT NOT NULL CHECK("religion_preference" IN ('Christianity', 'Islam', 'Judaism', 'Hinduism', 'Buddhism', 'Sikhism', 'Atheism/Agnosticism', 'Other', 'No Preference')),
	"bio"	TEXT NOT NULL,
	"top_1"	TEXT NOT NULL CHECK("top_1" IN ('clean', 'noise', 'sleep', 'guests', 'cook', 'major preference', 'religion preference', 'politics preference', 'greeklife', 'hobbies')),
	"top_2"	TEXT NOT NULL CHECK("top_2" IN ('clean', 'noise', 'sleep', 'guests', 'cook', 'major preference', 'religion preference', 'politics preference', 'greeklife', 'hobbies')),
	"top_3"	TEXT NOT NULL CHECK("top_3" IN ('clean', 'noise', 'sleep', 'guests', 'cook', 'major preference', 'religion preference', 'politics preference', 'greeklife', 'hobbies')),
	"profile_pic"	TEXT NOT NULL,
	PRIMARY KEY("userID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "user_accepted" (
	"userID"	INTEGER NOT NULL,
	"acceptedUserID"	INTEGER NOT NULL,
	FOREIGN KEY("acceptedUserID") REFERENCES "roommate_profiles"("userID") ON DELETE CASCADE,
	FOREIGN KEY("userID") REFERENCES "roommate_profiles"("userID") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "user_hobbies" (
	"userID"	INT NOT NULL,
	"hobbyID"	INT NOT NULL,
	PRIMARY KEY("userID","hobbyID"),
	FOREIGN KEY("hobbyID") REFERENCES "hobbies"("hobbyID"),
	FOREIGN KEY("userID") REFERENCES "roommate_profiles"("userID") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "user_rejections" (
	"userID"	INTEGER NOT NULL,
	"rejectedUserID"	INTEGER NOT NULL,
	FOREIGN KEY("rejectedUserID") REFERENCES "roommate_profiles"("userID") ON DELETE CASCADE,
	FOREIGN KEY("userID") REFERENCES "roommate_profiles"("userID") ON DELETE CASCADE
);
INSERT INTO "hobbies" VALUES (1,'Sports');
INSERT INTO "hobbies" VALUES (2,'Music');
INSERT INTO "hobbies" VALUES (3,'Gaming');
INSERT INTO "hobbies" VALUES (4,'Cooking');
INSERT INTO "hobbies" VALUES (5,'Reading');
INSERT INTO "hobbies" VALUES (6,'Traveling');

CREATE TRIGGER bio_update_trigger
AFTER UPDATE ON roommate_profiles
FOR EACH ROW
WHEN OLD.bio <> NEW.bio
BEGIN
    INSERT INTO bio_history (userID, bio, updated_at)
    VALUES (OLD.userID, OLD.bio, CURRENT_TIMESTAMP);
END;
COMMIT;

.save "roomie_match.db"