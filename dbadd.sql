USE formserver;

CREATE TABLE Counter(
	local int NULL,
	server int NULL);

CREATE TABLE Analytics(
	one int NULL,
	two int NULL,
	three int NULL,
	four int NULL);

INSERT INTO Counter VALUES(0,0);
