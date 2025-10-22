import Tyradex.API as API
import Tyradex.abc as abc
from Tyradex.TyradexErrors import TyradexError

__version__ = API.VERSION

class Pokemon:
    """ A Pokémon

    Attributes:
        pokedex_id (int): Pokédex ID
        generation (int): Generation
        category (str): Category
        name (abc.NameModel): Names
        sprites (abc.DetailedSpriteModel): Sprites
        types (list[abc.TypeModel]): Types
        talents (list[abc.TalentModel]): Talents
        stats (abc.StatModel): Stats
        resistances (list[abc.ResistanceModel]): Resistances
        evolutions (abc.EvolutionModel): Evolutions
        height (float): Height
        weight (float): Weight
        egg_groups (list[str]): Egg groups
        sexe (abc.SexeModel): Sexe
        catch_rate (int): Catch rate
        level_100 (int): Level 100
        formes (list[abc.RegionalFormModel]): Formes
    """

    @classmethod
    def all(cls):
        """ Get the list of different Pokémon.

        Returns:
            list[Pokemon]: The list of all Pokémon
        """
        response = API.Tyradex.call('pokemon')
        return [cls(**pokemon_data) for pokemon_data in (response if response else [])]

    @classmethod
    def get(cls, pokemon_id, region=..., talent=...):
        """ Get a Pokémon's information.

        Args:
            pokemon_id (str | int): The Pokémon's ID in the National Pokédex or its name.
            region (str): The Pokémon region. (Allows you to retrieve information on a Pokémon's regional form.)
            talent (str): The Pokémon's talent. (Allows you to recover the Pokémon's resistances based on its ability.)

        Returns:
            Pokemon: The Pokémon's information
        """
        endpoint = 'pokemon/{id_}'.format(id_=pokemon_id)
        if region is not ...:
            endpoint += '/{region}'.format(region=region)
        if talent is not ...:
            endpoint += '?talent={talent}'.format(talent=talent)
        return cls(**response) if (response := API.Tyradex.call(endpoint)) else None

    def __init__(self, **data):
        """ A Pokémon

        Args:
            pokedex_id (int): Pokédex ID
            generation (int): Generation
            category (str): Category
            name (dict): Names
            sprites (dict): Sprites
            types (list[dict]): Types
            talents (list[dict]): Talents
            stats (dict): Stats
            resistances (list[dict]): Resistances
            evolutions (dict): Evolutions
            height (str): Height
            weight (str): Weight
            egg_groups (list[str]): Egg groups
            sexe (dict): Sexe
            catch_rate (int): Catch rate
            level_100 (int): Level 100
            formes (list[dict]): Pokémon formes
        """
        self._pokedex_id = (pokedex_id if (pokedex_id := data.get('pokedex_id')) else -1)
        self._generation = (generation if (generation := data.get('generation')) else -1)
        self._category = str(data.get('category'))
        self._name = abc.NameModel(**data.get('name'))
        self._sprites = abc.DetailedSpriteModel(**(sprites if (sprites := data.get('sprites')) else {}))
        types = data.get('types')
        self._types = [abc.TypeModel(**type_data) for type_data in (types if types else [])]
        talents = data.get('talents')
        self._talents = [abc.TalentModel(**talent_data) for talent_data in (talents if talents else [])]
        self._stats = abc.StatModel(**(stats if (stats := data.get('stats')) else {}))
        resistances = data.get('resistances')
        self._resistances = [abc.ResistanceModel(**resistance_data) for resistance_data in (resistances if resistances else [])]
        self._evolutions = abc.EvolutionModel(**(evolutions if (evolutions := data.get('evolution')) else {}))
        self._height = height.split(' ')[0].replace(',', '.') if (height := data.get('height')) else 0.0
        self._weight = weight.split(' ')[0].replace(',', '.') if (weight := data.get('weight')) else 0.0
        self._egg_groups = egg_groups if (egg_groups := data.get('egg_groups')) else []
        self._sexe = abc.SexeModel(**(sexe if (sexe := data.get('sexe')) else {}))
        self._catch_rate = catch_rate if (catch_rate := data.get('catch_rate')) else 0
        self._level_100 = level_100 if (level_100 := data.get('level_100')) else -1
        formes = data.get('formes')
        self._formes = [abc.RegionalFormModel(**forme_data) for forme_data in (formes if formes else [])]

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return '<{id_}:{name}>'.format(id_=self._pokedex_id, name=self.name.en)

    @property
    def pokedex_id(self):
        """ Pokédex ID.

        Returns:
            int: Pokédex ID.
        """
        return self._pokedex_id

    @property
    def generation(self):
        """ Generation.
        
        Returns:
            int: Génération.
        """
        return self._generation
    
    @property
    def category(self):
        """ Category.

        Returns:
            str: Category.
        """
        return self._category

    @property
    def name(self):
        """ Name.
        
        Returns:
            abc.NameModel: Names.
        """
        return self._name
    
    @property
    def sprites(self):
        """ Sprites.

        Returns:
            abc.DetailedSpriteModel : Sprites.
        """
        return self._sprites

    @property
    def types(self):
        """ Types.
        
        Returns:
            list[abc.TypeModel]: Types.
        """
        return self._types
    
    @property
    def talents(self):
        """ Talents.

        Returns:
            list[abc.TalentModel]: Talents.
        """
        return self._talents

    @property
    def stats(self):
        """ Stats
        
        Returns:
            abc.StatModel: Stats.
        """
        return self._stats
    
    @property
    def resistances(self):
        """ Resistances.

        Returns:
            list[abc.ResistanceModel]: Resistances.
        """
        return self._resistances

    @property
    def evolutions(self):
        """ Evolutions.
        
        Returns:
            abc.EvolutionModel: Pokémon's evolutions.
        """
        return self._evolutions
    
    @property
    def height(self):
        """ Height.

        Returns:
            float: Pokémon height
        """
        return self._height

    @property
    def weight(self):
        """ Weight
        
        Returns:
            float: Pokémon weight
        """
        return self._weight
    
    @property
    def egg_groups(self):
        """ Egg groups

        Returns:
            abc.EggGroupModel: Egg groups.
        """
        return self._egg_groups

    @property
    def sexe(self):
        """ Sexe
        
        Returns:
            abc.SexeModel: Sexes.
        """
        return self._sexe
    
    @property
    def catch_rate(self):
        """ Catch rate

        Returns:
            int: Catch rate.
        """
        return self._catch_rate

    @property
    def level_100(self):
        """ Level 100
        
        Returns:
            int: How many xp for level 100.
        """
        return self._level_100
    
    @property
    def formes(self):
        """ Formes

        Returns:
            list[abc.RegionalFormModel]: Formes.
        """
        return self._formes

class Generation:
    """ Generation.

    Attributes:
        generation (int): Generation.
        from (int): Which index starts.
        to_ (int): Which index ended.
    """

    @classmethod
    def all(cls):
        """ Get the list of different generations

        Returns:
            list[Generation]: The list of all generation
        """
        response = API.Tyradex.call('gen')
        return [cls(**gen_data) for gen_data in (response if response else [])]

    @classmethod
    def get(cls, generation):
        """ Get the Generation.

        Args:
            generation (int): The generation number.

        Returns:
            Generation: The Generation's information.
        """
        generations = cls.all()
        if 0 < generation <= len(generations):
            return generations[generation - 1]
        else:
            raise TyradexError('Generation {generation} does not exist.'.format(generation=generation))

    def __init__(self, **data):
        """ Generation.

        Args:
            generation (int): Generation.
            from_ (int): Which index starts.
            to_ (int): Which index ended.
        """
        self._generation = generation if (generation := data.get('generation')) else -1
        self._from = from_ if (from_ := data.get('from')) else -1
        self._to = to if (to := data.get('to')) else -1

        raw_pokemons = API.Tyradex.call('gen/{id_}'.format(id_=self._generation))
        self._pokemons = [Pokemon(**pokemon_data) for pokemon_data in (raw_pokemons if raw_pokemons else [])]

    def __str__(self):
        return 'Gen {gen}'.format(gen=self._generation)

    def __repr__(self):
        return '<gen {g} from {f} to {t}>'.format(g=self._generation, f=self._from, t=self._to)

    @property
    def generation(self):
        """ Generation.

        Returns:
            int: Generation.
        """
        return self._generation

    @property
    def from_(self):
        """ Which index starts.

        Returns:
            int: Which index started.
        """
        return self._from

    @property
    def to_(self):
        """ Which index ended.

        Returns:
            int: Which index ended
        """
        return self._to

    @property
    def pokemons(self):
        """ Pokémon.

        Returns:
            list[Pokemon]: Pokémon.
        """
        return self._pokemons

class Type:
    """ Type.

    Attributes:
        type_id (int): Type ID.
        name (abc.NameModel): Names.
        sprites (string): Sprites.
        resistances (list[abc.ResistanceModel]): Resistances.
        pokemons (list[Pokemon]): All Pokémon of this type.
    """

    @classmethod
    def all(cls):
        """ Get the list of all types.

        Returns:
            list[Type]: The list of all types.
        """
        response = API.Tyradex.call('types')
        return [cls(**type_data) for type_data in (response if response else [])]

    @classmethod
    def get(cls, type_1, type_2=...):
        """ Get the list of Pokémon of a generation.

        Args:
            type_1 (int | str): The First type identifier, or its English or French name.
            type_2 (int | str): The Second type identifier, or its English or French name.

        Returns:
            Type: The Type
        """
        if type_1 == type_2:
            type_2 = ...
        elif type_2 is not ...:
            type_1, type_2 = sorted((type_1, type_2))
        endpoint = 'types/{type_1}'.format(type_1=type_1)
        if type_2 is not ...:
            endpoint += '/{type_2}'.format(type_2=type_2)
        return Type(**(type_ if (type_ := API.Tyradex.call(endpoint)) else {}))

    def __init__(self, **data):
        """ Type.

        Attributes:
            type_id (int): Type ID.
            name (dict): Names.
            sprites (string): Sprites.
            resistances (list[dict]): Resistances.
            pokemons (list[dict]): All Pokémon of this type.
        """
        self._type_id = id_ if (id_ := data.get('type_id')) else -1
        self._name = abc.NameModel(**(names if (names := data.get('name')) else {}))
        self._sprites = sprites if (sprites := data.get('sprites')) else abc.DEFAULT_IMG
        resistances = data.get('resistances')
        self._resistances = [abc.ResistanceModel(**resistance_data) for resistance_data in (resistances if resistances else [])]
        pokemon = data.get('pokemons')
        self._pokemons = [Pokemon(**pokemon_data) for pokemon_data in (pokemon if pokemon else [])]

    def __str__(self):
        return str(self._name)

    def __repr__(self):
        return '<{id_}:{name}>'.format(id_=self._type_id, name=self.name.en)

    @property
    def type_id(self):
        """ Type ID.

        Returns:
            int: Type ID.
        """
        return self._type_id

    @property
    def name(self):
        """ Names.

        Returns:
            abc.NameModel: Names.
        """
        return self._name

    @property
    def sprites(self):
        """ Sprites.

        Returns:
            str: Sprites.
        """
        return self._sprites

    @property
    def resistances(self):
        """ Resistances.

        Returns:
            list[abc.ResistanceModel]: Resistances.
        """
        return self._resistances

    @property
    def pokemons(self):
        """ Pokémon.

        Returns:
            list[Pokemon]: Pokémon.
        """
        return self._pokemons



if __name__ == '__main__':
    pass
