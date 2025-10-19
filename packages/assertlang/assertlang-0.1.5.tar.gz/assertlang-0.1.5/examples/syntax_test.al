// AssertLang Syntax Test File
// This file tests all syntax highlighting features

// Contract decorators
@requires str.length(name) > 0
@ensures result.is_ok()
@invariant count >= 0

// Function with type annotations
function createUser(name: string, email: string) -> Result<User, Error> {
    // Stdlib function highlighting
    if (str.length(name) < 1) {
        return Err("Name cannot be empty");
    }

    if (!str.contains(email, "@")) {
        return Err("Invalid email format");
    }

    // Number formats
    let hex_id = 0xFF;
    let binary_flags = 0b1010;
    let octal_perms = 0o755;
    let float_score = 3.14159;
    let scientific = 2.5e10;

    // String escapes
    let message = "Hello\nWorld\t\"Quoted\"\u0041";

    // Option and Result types
    let user: Option<User> = Some(User {
        id: hex_id,
        name: name,
        email: email
    });

    // Pattern matching
    match user {
        Some(u) => return Ok(u),
        None => return Err("User creation failed")
    }
}

// List operations
function processUsers(users: List<User>) -> Result<List<string>, Error> {
    let names = list.map(users, |u| u.name);
    let filtered = list.filter(names, |n| str.length(n) > 0);
    return Ok(filtered);
}

// Map operations
function getUserMap() -> Map<int, User> {
    let users: Map<int, User> = map.new();
    map.set(users, 1, User { id: 1, name: "Alice", email: "alice@example.com" });
    return users;
}

// Set operations
function getActiveUsers(allUsers: Set<User>, inactiveUsers: Set<User>) -> Set<User> {
    return set.difference(allUsers, inactiveUsers);
}

// Built-in functions
function debug_info(value: any) {
    print("Debug: ");
    println(value);
    assert(value != null);
    debug(format("Value: {}", value));
    let ts = timestamp();
}

// Constants and keywords
let is_active: bool = true;
let is_deleted: bool = false;
let empty: Option<string> = None;
let result: Result<int, string> = Ok(42);

// Control flow
for (user in users) {
    if (user.is_active) {
        continue;
    } else {
        break;
    }
}

while (count > 0) {
    count = count - 1;
}

// Error handling
try {
    throw Error("Something went wrong");
} catch (e) {
    panic("Critical error");
} finally {
    println("Cleanup");
}

// Operators
let sum = a + b;
let diff = a - b;
let product = a * b;
let quotient = a / b;
let remainder = a % b;

let is_equal = a == b;
let not_equal = a != b;
let less = a < b;
let greater = a > b;
let less_eq = a <= b;
let greater_eq = a >= b;

let and_result = a && b;
let or_result = a || b;
let not_result = !a;

// Arrow operators
let lambda = (x: int) => x * 2;
let arrow_return = (x: int) -> int { return x + 1; };

// Self reference
class User {
    function getName(self) -> string {
        return self.name;
    }
}
