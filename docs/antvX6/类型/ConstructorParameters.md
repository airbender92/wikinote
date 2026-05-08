TypeScript Constructor Parameter Types

In TypeScript, you can extract the parameter types of a class constructor using the built-in utility type ConstructorParameters<Type>. This is useful when you want to reuse constructor argument types without redefining them.

Example:

```ts
class User {
constructor(public name: string, public age: number) {}
}

// Extract constructor parameter types as a tuple
type UserConstructorParams = ConstructorParameters<typeof User>;
// type UserConstructorParams = [string, number]

// Use extracted types in a function
function createUser(...args: UserConstructorParams): User {
return new User(...args);
}

const u1 = createUser("Alice", 30); // ✅ Works
const u2 = createUser("Bob", "thirty"); // ❌ Error: 'string' is not assignable to 'number'
```
How it works:

ConstructorParameters<Type> takes a constructor function type and returns a tuple of its parameter types.

You must pass the type of the class itself, not an instance type — hence typeof ClassName.

Another example with different parameter types:

```ts
class Rectangle {
constructor(public width: number, public height: number) {}
}

type RectParams = ConstructorParameters<typeof Rectangle>;
// [number, number]

function makeRectangle(...params: RectParams): Rectangle {
return new Rectangle(...params);
}

const r1 = makeRectangle(10, 20); // ✅
const r2 = makeRectangle(10); // ❌ Missing parameter
```
Key points to remember:

Always use typeof ClassName when passing to ConstructorParameters.

The returned tuple can be indexed (e.g., ConstructorParameters<typeof MyClass>[0]) to get a specific parameter type.

Works with classes and constructor signatures in interfaces.

This approach ensures type safety and avoids duplication when working with class constructors.