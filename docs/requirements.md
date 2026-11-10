### Story ID: US-01 — User Registration

As a user, I want to create a new account, so that I can login later with the correct credentials.

Acceptance Criteria:

- [] If the user puts a new email + strong password while registering, it will give a 201 and the user will be able to log in.
- [] If the user uses a duplicate email, then it will give a 409 and show actionable message to the user.

### Story ID: US-02 — User login and logout

As a user I want to sign in into the system so that access it. As a user I want to sign out from the system so that I can remove access.

Acceptance Criteria:

- [] Successful sign in will let the user access the system.
- [] Protected endpoints will reject unauthenticated requests with 401.
- [] Logout invalidates session and client-side token. It will also remove document access.

### Story ID: US-03 — Upload PDF
