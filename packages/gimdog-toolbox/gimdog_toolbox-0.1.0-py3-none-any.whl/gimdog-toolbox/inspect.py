import inspect


def inspect_object(obj):
    """Inspect an object and print its attributes, methods, and properties."""
    print("Type:", type(obj))

    print("\n__dict__:")
    try:
        for k, v in vars(obj).items():
            print(f"  {k}: {type(v)}")
    except TypeError:
        print("  (no __dict__)")

    print("\nAll attributes (dir):")
    for name in dir(obj):
        if name.startswith("__"):
            continue
        print(" ", name)

    print("\nCallable members and signatures:")
    for name, member in inspect.getmembers(obj, predicate=callable):
        if name.startswith("__"):
            continue
        try:
            sig = inspect.signature(member)
        except (ValueError, TypeError):
            sig = "(...)"
        print(" ", name, sig)

    print("\nProperties on class:")
    for name, member in inspect.getmembers(obj.__class__):
        if isinstance(member, property):
            try:
                val = getattr(obj, name)
            except Exception as e:
                val = f"<error: {e}>"
            print(" ", name, "=", val)