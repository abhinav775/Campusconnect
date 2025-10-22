-- ----------------------------
-- Students Table
-- ----------------------------
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    class TEXT NOT NULL,
    admissionNo TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    phone TEXT NOT NULL
);

-- ----------------------------
-- Admins Table
-- ----------------------------
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- ----------------------------
-- Clubs Table
-- ----------------------------
CREATE TABLE IF NOT EXISTS clubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    banner TEXT
);

-- ----------------------------
-- Events Table
-- ----------------------------
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    host TEXT NOT NULL,
    description TEXT
);

-- ----------------------------
-- Event Registrations Table
-- ----------------------------
CREATE TABLE IF NOT EXISTS event_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    UNIQUE(student_id, event_id),
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE CASCADE
);

-- ----------------------------
-- Club Memberships Table
-- ----------------------------
CREATE TABLE IF NOT EXISTS club_memberships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    club_id INTEGER NOT NULL,
    UNIQUE(student_id, club_id),
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(club_id) REFERENCES clubs(id) ON DELETE CASCADE
);
