def singleton(cls):
    """A decorator to make a class a thread safe Singleton.
    HOW TO USE - 
    Add @singleton above the class you wish to be the singleton
    Example - 
    
    @singleton
    class DBConnection:
        <classmethods here>
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
