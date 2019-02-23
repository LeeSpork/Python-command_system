"""
by LeeSpork

An extendable command system.

date first created: 2019-2-22
date last modified: 2019-2-23

version name: 1.0
"""

#==============================================================================#
#====================[ Objects ]===============================================#
#==============================================================================#

class Command_System:
    """Class for the command system object.

    Idealy, there probably should be exactly 1 Command_System object.
    """

    #=== Command_System Exceptions ===============================

    class Bad_Command_Arguments_Error(Exception):
        """Raise this in your custom command function when the arguments are bad.

        e.g. 'if len(arguments) == 0: raise command_system.Bad_Command_Arguments_Error'
        """
        pass
    
    class Unknown_Command_Error(Exception):
        """Used internally by Command_System; don't worry about this."""
        pass

    #=== Command_System (sub-?) Objects ===============================
    
    class Command:
        """Class for objects that represent commands.

        It is recommeneded that you don't create them manually;
        use Command_System.define_command instead.
        """
        def __init__(self, name, function, permission_level, aliases, usage, description, parent_command_system):
            self.name = name
            self.aliases = aliases
            self.function = function
            self.permission_level = permission_level
            self.usage = usage
            self.description = description
            self.parent = parent_command_system
        
        def run(self, user, args:list):
            try: return self.function(user, args) #Run the command:
            
            #If the bad arguments error was raised, tell the user our usage:
            except self.parent.Bad_Command_Arguments_Error:

                output = "Error: bad arguments."
                if self.usage != None:
                    output += " Usage: {}".format(self.get_usage())
                
                return self.parent.tell_user(user, output)

        def get_usage(self) -> str:
            return "{} {}".format(self.name, self.usage)

    #=== Command_System Methods ===============================
    
    def __init__(self, case_sensitive=False, help_aliases:list=None):
        """Create a Command System.
        
        Set case_sensitive to True if you want things like "Cmd" being different to "cmd".
        Use a list of strings for help_aliases to add aliases for the built-in
        "help" command.
        """
        self.commands = {}
        self.command_aliases = {}
        self.case_sensitive = case_sensitive

        #Define built-in commands
        if help_aliases == None: help_aliases = []
        self.define_command(
            "help", self.help_command, 0, ["?"] + help_aliases,"[command]",
            "A built-in command system command. Returns a list of commands, or information on a specific command."
            )

    def define_command (
        self, name:str, function, permission_level:int=0, aliases:list=None,
        usage:str=None, description:str=None
        ):
        """Creates a command for this command system."""

        #Create the command:
        new_cmd = self.Command(name, function, permission_level, aliases, usage, description, self)
        self.commands[self.casefix(name)] = new_cmd #Store it here for safe keeping
        
        #Remember it's aliases:
        if aliases == None: pass #No aliases
        elif isinstance(aliases, str): #One alias, passed as a str
            self.command_aliases[aliases] = new_cmd
        else:
            #Assume that it's a list or tuple or something if it got here
            for i in aliases:
                self.command_aliases[self.casefix(i)] = new_cmd

        return new_cmd #Return it just in case someone needs it idk

    def get_command(self, command_name):
        """Returns a command object from it's name or alias."""
        try: return self.commands[command_name]
        except KeyError:
            try: return self.command_aliases[command_name]
            except KeyError:
                raise self.Unknown_Command_Error

    def run_command(self, user, command_name:str, arguments:list):
        """Most important method! Call this when the user says a command."""

        #Try to find the command in the list of commands/command aliases:
        try:
            this_cmd = self.get_command(self.casefix(command_name))
            
        except self.Unknown_Command_Error:
            #No command was found, tell the user this:
            return self.tell_user(user, "Unknown command. Try 'help' for a list of commands")
        
        if this_cmd.permission_level > user.get_command_permission_level():
            #User has insufficent permsissions, tell them this:
            return self.tell_user(user, "Error: You do not have permission to use this command.")

        else: return this_cmd.run(user, arguments) #Run command

    def casefix(self, string):
        """Used to ensure lowercase words if the command system is not in case-sensitive mode.""" 
        if self.case_sensitive:
            return string
        else:
            return string.lower()

    def tell_user(self, user, something):
        """Function used to tell the user things.

        e.g. "missing command", "missing perms", or the output of the help command, etc.
        It is a good idea to override this.
        """
        print(something)
    
    def help_command(self, user, args):
        """Function for the help/? command. Feel free to override."""
        #Prints a list of all commands if there was no arguments
        if len(args) == 0:
            output = "Commands:"
            for i in self.commands:
                output += "\n" + i
            return self.tell_user(user, output)

        #If there was an arugment
        else:
            #Tell the user the help for the command:
            try: return self.tell_user(user, self.get_command_info(
                    self.get_command(self.casefix(args[0]))
                ))
            #If it turns out that actually that command didn't exist:
            except self.Unknown_Command_Error:
                return self.tell_user(user,
                        "Unknown command '{}'".format(self.casefix(args[0])))
                

    def get_command_info(self, command):
        """Used for the default help_command function. Seperated in case you wanted to override it."""

        output ="Help for {}:".format(command.name)
                
        output +="\nUsage: "
        if command.usage == None: output += "(usage not defined)"
        else: output += command.get_usage()
        
        output +="\nAliases: "
        if command.aliases == None or len(command.aliases) == 0:
            output += "(none)"
        else:
            output += command.aliases[0]
            for i in range(1, len(command.aliases)):
                output += ", " + command.aliases[i]

        output +="\nDecription: "
        if command.description == None: output += "(description not defined)"
        else: output += "\n" + command.description
        
        return output

#==============================================================================#
#====================[ "Main" code ]===========================================#
#==============================================================================#

if __name__ == "__main__":

    #example user class
    class User:
        """Example user class. Instances of this represent users of the command system."""
        def __init__(self, name="Nameless user"):
            self.name = name
            self.permission_level = 0
        def get_command_permission_level(self):
            return self.permission_level

    #Create a functions to later use for a command
    def say_command(user, args):
        if len(args) == 0: raise command_system.Bad_Command_Arguments_Error
        else: print(*args)  # You could use a for loop to print all the args,
                            # but this works too :P
    def example_command_2(user, args):
        if len(args) != 0 and args[0][0] == '-':
            raise command_system.Bad_Command_Arguments_Error
        print(args)

    # Create a new command system:
    command_system = Command_System()
    # Define a new command:
    command_system.define_command (
        "say", say_command, permission_level=0, aliases=[],
        usage="<words>", description="Example command, prints words"
        )
    # Define a command the bare minimum way:
    command_system.define_command("wow", example_command_2)
    # Admin-only command:
    command_system.define_command("egg", example_command_2, permission_level=100)

    print("Welcome my command system demo thing!\
\nUse 'help' for a list of commands.")

    local_user = User()
    while True:
        words = input("\nCommand >").split()
        command_system.run_command(local_user, words[0], words[1:])

# teh end
