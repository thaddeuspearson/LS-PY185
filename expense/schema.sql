CREATE TABLE expenses (
    id serial PRIMARY KEY,
    amount numeric(6, 2) NOT NULL CHECK (amount > 0),
    memo text NOT NULL,
    created_on date NOT NULL
);

INSERT INTO expenses (amount, memo, created_on)
       VALUES (14.56, 'Pencils', NOW()),
              (3.29, 'Coffee', NOW()),
              (49.99, 'Text Editor', NOW());