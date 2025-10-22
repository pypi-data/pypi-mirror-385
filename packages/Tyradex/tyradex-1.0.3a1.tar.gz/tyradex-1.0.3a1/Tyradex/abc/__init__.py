"""
ABC module

All schema for Tyradex.
"""
import locale

DEFAULT_IMG = "https://raw.githubusercontent.com/LassaInora/Tyradex/refs/heads/images/clone.png"

class NameModel:
    """ A multilingual name

    Attributes:
        fr (str): French name.
        en (str): English name.
        jp (str): Japan name.
    """
    def __init__(self, **data):
        """ A multilingual name.

        Args:
            fr (str): French name.
            en (str): English name.
            jp (str): Japan name.
        """
        self._fr = data.get('fr')
        self._en = data.get('en')
        self._jp = data.get('jp')

    def __str__(self):
        if (l := locale.getlocale()[0][:2]) == "fr":
            return ', '.join(self._fr) if isinstance(self._fr, list) else str(self._fr)
        elif l == "ja":
            return ', '.join(self._jp) if isinstance(self._jp, list) else str(self._jp)
        else:
            return ', '.join(self._en) if isinstance(self._en, list) else str(self._en)

    @property
    def fr(self):
        """ The French name.

        Returns:
            str: French name.
        """
        return self._fr

    @property
    def en(self):
        """ The English name.

        Returns:
            str: English name.
        """
        return self._en

    @property
    def jp(self):
        """ The Japan name.

        Returns:
            str: Japan name.
        """
        return self._jp

class SimpleSpriteModel:
    """ A simple sprite.

    Attributes:
        regular (str): Regular sprite.
        shiny (str): Shiny sprite.

    """

    def __init__(self, **data):
        """ A simple sprite.

        Args:
            regular (str): Regular sprite.
            shiny (str): Shiny sprite.
        """
        self._regular = sprite if (sprite := data.get('regular')) else DEFAULT_IMG
        self._shiny = sprite if (sprite := data.get('shiny')) else DEFAULT_IMG

    @property
    def regular(self):
        """ The regular sprite.

        Returns:
            str: Regular sprite.
        """
        return self._regular

    @property
    def shiny(self):
        """ The shiny sprite.

        Returns:
            str: Shiny sprite.
        """
        return self._shiny

class DetailedSpriteModel:
    """ A detailed sprite.

    Attributes:
        regular (str): Regular sprite.
        shiny (str): Shiny sprite.
        gmax (SimpleSpriteModel): GigaMax sprites.
    """

    def __init__(self, **data):
        """ A detailed sprite model.

        Args:
            regular (str): Regular sprite.
            shiny (str): Shiny sprite.
            gmax (dict): GigaMax sprites.
        """
        self._regular = sprite if (sprite := data.get('regular')) else DEFAULT_IMG
        self._shiny = sprite if (sprite := data.get('shiny')) else DEFAULT_IMG
        self._gmax = SimpleSpriteModel(**(gmax if (gmax := data.get('gmax')) else {}))

    @property
    def regular(self):
        """ The regular sprite.

        Returns:
            str: Regular sprite.
        """
        return self._regular

    @property
    def shiny(self):
        """ The shiny sprite.

        Returns:
            str: Shiny sprite.
        """
        return self._shiny

    @property
    def gmax(self):
        """ The GigaMax sprite.

        Returns:
            str: GigaMax sprite.
        """
        return self._gmax

class TypeModel:
    """ A type

    Attributes:
        name (str): Name.
        image (str): Image.
    """

    def __init__(self, **data):
        """ A type.

        Args:
            name (str): Name.
            image (str): Image.
        """
        self._name = str(data.get('name'))
        self._image = sprite if (sprite := data.get('image')) else DEFAULT_IMG

    @property
    def name(self):
        """ Name.

        Returns:
            str: Name.
        """
        return self._name

    @property
    def image(self):
        """ Image.

        Returns:
            str: Image.
        """
        return self._image

class TalentModel:
    """ A talent

    Attributes:
        name (str): Name.
        tc (bool): Is hidden talent.
    """

    def __init__(self, **data):
        """ A talent

        Args:
            name (str): Name.
            tc (bool): Is hidden talent.
        """
        self._name = str(data.get('name'))
        self._tc = tc if (tc := data.get('tc')) else False

    @property
    def name(self):
        """ Name.

        Returns:
            str: Name.
        """
        return self._name

    @property
    def tc(self):
        """ Is hidden talent.

        Returns:
            bool: Is hidden talent.
        """
        return self._tc

class StatModel:
    """ A stats.

    Attributes:
        hp (int): The health points.
        atk (int): The attack points.
        def (int): The defense points.
        spe_atk (int): The special attack points.
        spe_def (int): The special defense points.
        vit (int): The vitesse points.
    """

    def __init__(self, **data):
        """ A stats.

        Args:
            hp (int): The health points.
            atk (int): The attack points.
            def (int): The defense points.
            spe_atk (int): The special attack points.
            spe_def (int): The special defense points.
            vit (int): The vitesse points.
        """
        self._hp = hp_ if (hp_ := data.get('hp')) else 0
        self._atk = atk_ if (atk_ := data.get('atk')) else 0
        self._def = def_ if (def_ := data.get('def')) else 0
        self._spe_atk = spe_atk_ if (spe_atk_ := data.get('spe_atk')) else 0
        self._spe_def = spe_def_ if (spe_def_ := data.get('spe_def')) else 0
        self._vit = vit_ if (vit_ := data.get('vit')) else 0

    @property
    def hp(self):
        """ The health points.

        Returns:
            int: health points
        """
        return self._hp

    @property
    def atk(self):
        """ The attack points.

        Returns:
            int: attack points
        """
        return self._atk

    @property
    def def_(self):
        """ The defense points.

        Returns:
            int: defense points
        """
        return self._def

    @property
    def spe_atk(self):
        """ The special attack points.

        Returns:
            int: special attack points
        """
        return self._spe_atk

    @property
    def spe_def(self):
        """ The special defense points.

        Returns:
            int: special defense points
        """
        return self._spe_def

    @property
    def vit(self):
        """ The vitesse points.

        Returns:
            int: vitesse points
        """
        return self._vit

class ResistanceModel:
    """ Resistance.

    Attributes:
        name (str): Name.
        multiplier (float): Multiplier.
    """

    def __init__(self, **data):
        """ Resistance.

        Args:
            name (str): Name.
            multiplier (float): Multiplier.
        """
        self._name = str(data.get('name'))
        self._multiplier = multiplier if (multiplier := data.get('multiplier')) else 1

    @property
    def name(self):
        """ Name.

        Returns:
            str: Name.
        """
        return self._name

    @property
    def multiplier(self):
        """ Multiplier.

        Returns:
            float: Multiplier.
        """
        return self._multiplier

class PokemonEvolutionModel:
    """ Pokémon evolution.

    Attributes:
        pokedex_id (int): Pokédex ID.
        name (str): Name.
        condition (str): Conditions.
    """

    def __init__(self, **data):
        """ Pokémon evolution.

        Args:
            pokedex_id (int): Pokédex ID.
            name (str): Name.
            condition (str): Conditions.
        """
        self._pokedex_id = pokedex_id if (pokedex_id := data.get('pokedex_id')) else -1
        self._name = str(data.get('name'))
        self._condition = str(data.get('condition'))

    def __str__(self):
        return f"{self.name} ({self.condition})"

    def __repr__(self):
        return self.name

    @property
    def pokedex_id(self):
        """ Pokédex ID.

        Returns:
            int: Pokédex ID.
        """
        return self._pokedex_id

    @property
    def name(self):
        """ Name.

        Returns:
            str: Name.
        """
        return self._name

    @property
    def condition(self):
        """ Condition.

        Returns:
            str: Condition.
        """
        return self._condition

class MegaEvolutionModel:
    """ Mega evolution.

    Attributes:
        name (str): Names.
        orbes (list[str]): Orbes.
        sprites (SimpleSpriteModel): Sprites.
    """

    def __init__(self, **data):
        """ Mega evolution.

        Args:
            name (str): Names.
            orbes (list[str]): Orbes.
            sprites (dict): Sprites.
        """
        self._name = str(data.get('name'))
        self._orbes = orbes if (orbes := data.get('orbe')) else []
        self._sprites = SimpleSpriteModel(**(sprites if (sprites := data.get('sprites')) else {}))

    def __str__(self):
        return f"{self.name} ({self.orbes})"

    def __repr__(self):
        return self.name

    @property
    def name(self):
        """ Name.

        Returns:
            str: Name.
        """
        return self._name

    @property
    def orbes(self):
        """ Orbes.

        Returns:
            list[str]: Orbes.
        """
        return self._orbes

    @property
    def sprites(self):
        """ Sprites.

        Returns:
            SimpleSpriteModel: Sprites.
        """
        return self._sprites

class EvolutionModel:
    """ Evolution.

    Attributes:
        pre (list[PokemonEvolutionModel]): Pre-Evolutions.
        next (list[PokemonEvolutionModel]): Next-Evolutions.
        mega (list[MegaEvolutionModel]): Mega-Evolutions.
    """

    def __init__(self, **data):
        """ Evolution.

        Args:
            pre (list[dict]): Pre-Evolutions.
            next (list[dict]): Next-Evolutions.
            mega (list[dict]): Mega-Evolutions.
        """
        list_pre = data.get('pre')
        self._pre = [PokemonEvolutionModel(**pre) for pre in (list_pre if list_pre else [])]
        list_next = data.get('next')
        self._next = [PokemonEvolutionModel(**next_) for next_ in (list_next if list_next else [])]
        list_mega = data.get('mega')
        self._mega = [MegaEvolutionModel(**mega) for mega in (list_mega if list_mega else [])]

    def __str__(self):
        p = ', '.join([str(p) for p in self._pre])
        n = ', '.join([str(p) for p in self._next])
        m = ', '.join([str(p) for p in self._mega])
        return (f"{p}, " if p else "") + "[X]" + (f", {n}" if n else "") + (f", {m}" if m else "")

    def __repr__(self):
        p = ', '.join([repr(p) for p in self._pre])
        n = ', '.join([repr(p) for p in self._next])
        m = ', '.join([repr(p) for p in self._mega])
        return '[' + (f"{p}, " if p else "") + "[X]" + (f", {n}" if n else "") + (f", {m}" if m else "") + ']'

    @property
    def pre(self):
        """ Pre-Evolutions.

        Returns:
            list[PokemonEvolutionModel]: Pre-Evolutions.
        """
        return self._pre

    @property
    def next(self):
        """ Next-Evolutions.

        Returns:
            list[PokemonEvolutionModel]: Next-Evolutions.
        """
        return self._next

    @property
    def mega(self):
        """ Mega-Evolutions.

        Returns:
            list[PokemonEvolutionModel]: Mega-Evolutions.
        """
        return self._mega

class SexeModel:
    """ Sexe.

    Attributes:
        male (float): Pourcentage of male.
        female (float): Pourcentage of female.
    """

    def __init__(self, **data):
        """ Sexe.

        Args:
            male (float): Pourcentage of male.
            female (float): Pourcentage of female.
        """
        self._male = male if (male := data.get('male')) else 0.0
        self._female = female if (female := data.get('female')) else 0.0

    @property
    def male(self):
        """ Pourcentage of male.

        Returns:
            float: Pourcentage of male.
        """
        return self._male

    @property
    def female(self):
        """ Pourcentage of female.

        Returns:
            float: Pourcentage of female.
        """
        return self._female

class RegionalFormModel:
    """ Regional form

    Attributes:
        region (str): Region.
        name (NameModel): Name.
    """

    def __init__(self, **data):
        """ Regional form

        Args:
            region (str): Region.
            name (dict): Name.
        """
        self._region = str(data.get('region'))
        self._name = NameModel(**(name if (name := data.get('name')) else {}))

    @property
    def region(self):
        """ Region.

        Returns:
            str: Region.
        """
        return self._region

    @property
    def name(self):
        """ Name.

        Returns:
            NameModel: Name.
        """
        return self._name