
# Author: Pearu Peterson
# Created: April 2011

__all__ = ['load_stoic_from_sbml',
           'load_stoic_from_text',
           ]

import re
from collections import defaultdict

from .utils import obj2num


def load_stoic_from_sbml(file_name):
    """ Return stoichiometry information of a network described in a SBML file.

    Parameters
    ----------
    file_name : str
      Path to SMBL file.

    Returns
    -------
    matrix : dict
      A stoichiometry matrix defined as mapping {(species, reaction): stoichiometry}.
    species : list
      A list of species names.
    reactions : list
      A list of reaction names.
    species_info : dict
    reactions_info : dict
    """
    from lxml import etree
    tree = etree.parse(file_name)
    root = tree.getroot()
    assert root.tag.endswith ('sbml'), `root.tag`
    version = int(root.attrib['version'])
    level = int(root.attrib['level'])
    if level in [2,3]:
        default_stoichiometry = '1'
    else:
        default_stoichiometry = None
    compartments = {}
    species = []
    modifiers = []
    species_all = []
    reactions = []
    species_reactions = defaultdict (lambda:[])
    reactions_species = defaultdict (lambda:[])
    reactions_info = defaultdict(lambda:dict(modifiers=[],reactants=[],products=[],
                                            boundary_specie_stoichiometry={},annotation=[],
                                            compartments = set()))
    species_info = defaultdict(lambda:dict())
    matrix = {}
    for model in root:
        for item in model:
            if item.tag.endswith('listOfCompartments'):
                for compartment in item:
                    compartments[compartment.attrib['id']] = compartment.attrib
            elif item.tag.endswith('listOfSpecies'):
                for specie in item:
                    species_all.append(specie.attrib['id'])
                    species_info[specie.attrib['id']]['compartment'] = specie.attrib['compartment']
                    species_info[specie.attrib['id']]['name'] = specie.attrib['name']
            elif item.tag.endswith('listOfReactions'):
                for reaction in item:
                    reaction_id = reaction.attrib['id']
                    assert reaction_id not in reactions,`reaction_id`
                    reactions.append(reaction_id)
                    reaction_index = len(reactions)-1
                    reactions_info[reaction_id]['name'] = reaction.attrib['name']
                    reactions_info[reaction_id]['reversible'] = eval(reaction.attrib.get('reversible', 'False').title())
                    for part in reaction:
                        if part.tag.endswith ('listOfReactants'):
                            for reactant in part:
                                assert reactant.tag.endswith('speciesReference'), `reactant.tag`
                                specie_id = reactant.attrib['species']
                                stoichiometry = -obj2num(reactant.attrib.get('stoichiometry', default_stoichiometry))
                                reactions_info[reaction_id]['reactants'].append(specie_id)
                                try:
                                    specie_index = species.index(specie_id)
                                except ValueError:
                                    species.append(specie_id)
                                    specie_index = len(species)-1
                                assert stoichiometry,`stoichiometry`
                                matrix[specie_index, reaction_index] = stoichiometry
                                species_reactions[specie_index].append(reaction_index)
                                reactions_species[reaction_index].append(specie_index)                                
                                reactions_info[reaction_id]['compartments'].add(species_info[specie_id]['compartment'])
                        elif part.tag.endswith ('listOfProducts'):
                            for product in part:
                                assert product.tag.endswith('speciesReference'), `product.tag`
                                specie_id = product.attrib['species']
                                stoichiometry = obj2num(product.attrib.get('stoichiometry', default_stoichiometry))
                                reactions_info[reaction_id]['products'].append(specie_id)
                                try:
                                    specie_index = species.index(specie_id)
                                except ValueError:
                                    species.append(specie_id)
                                    specie_index = len(species)-1
                                assert stoichiometry,`stoichiometry`
                                matrix[specie_index, reaction_index] = stoichiometry
                                species_reactions[specie_index].append(reaction_index)
                                reactions_species[reaction_index].append(specie_index)
                                reactions_info[reaction_id]['compartments'].add(species_info[specie_id]['compartment'])
                        elif part.tag.endswith ('listOfModifiers'):
                            for modifier in part:
                                assert modifier.tag.endswith('modifierSpeciesReference'), `modifier.tag`
                                specie_id = product.attrib['species']
                                reactions_info[reaction_id]['modifiers'].append(specie_id)
                                reactions_info[reaction_id]['compartments'].add(species_info[specie_id]['compartment'])
                            continue
                        elif part.tag.endswith ('annotation'):
                            reactions_info[reaction_id]['annotation'].append(part.text)
                            continue
                        elif re.match(r'.*(kineticLaw|notes)\Z', part.tag):                            
                            continue
                        else:
                            print 'get_stoichiometry:warning:unprocessed reaction element: %r' % (part.tag)
                            continue


            elif re.match (r'.*(annotation|notes|listOfSpeciesTypes|listOfUnitDefinitions)\Z', item.tag):
                pass
            else:
                print 'get_stoichiometry:warning:unprocessed model element: %r' % (item.tag)

    return matrix, species, reactions, species_info, reactions_info
    

def load_stoic_from_text(text):
    """ Parse stoichiometry matrix from a string.

    Parameters
    ----------
    text : str

      A multiline string where each line contains a chemical reaction
      description. The description must be given in the following
      form: ``<sum of reactants> (=> | <=) <sum of producats>``. For example,
      ``A + 2*B => C``. Lines starting with ``#`` are ignored.

    Returns
    -------
    matrix_data : dict
      A dictionary representing a stoichiometry matrix.

    species : list
      A list of row names.

    reactions : list
      A list of column names.

    species_info : dict
    reactions_info : dict
    """
    #TODO: fill up species_info and reactions_info dictionaries

    def _split_sum (line):
        for part in line.split('+'):
            part = part.strip()
            coeff = ''
            while part[0].isdigit():
                coeff += part[0]
                part = part[1:].lstrip()
            if not coeff:
                coeff = '1'
            yield part, eval (coeff)

    matrix = {}
    reactions = []
    species = []
    reactions_info = defaultdict(lambda:dict(modifiers=[],reactants=[],products=[],
                                            boundary_specie_stoichiometry={},annotation=[],
                                            compartments = set()))
    species_info = defaultdict(lambda:dict())
    for line in text.splitlines():
        if not line.strip () or line.startswith ('#'): continue
        reversible = False
        left, right = line.split ('=')
        direction = '='
        if right.startswith('>'):
            right = right[1:].strip()
            direction = '>'
            if left.endswith ('<'):
                left = left[:-1].strip()
                reversible = True
        elif left.endswith ('>'):
            left = left[:-1].strip()
            direction = '>'
        elif left.endswith ('<'):
            left = left[:-1].strip()
            direction = '<'
        elif right.startswith ('<'):
            right = right[1:].strip()
            direction = '<'



        left_specie_coeff = list(_split_sum(left))
        right_specie_coeff = list(_split_sum(right))
        left_specie_names = [n for n,c in left_specie_coeff]
        right_specie_names = [n for n,c in right_specie_coeff]

        if direction=='<':
            reaction_name = 'R_%s_%s' % (''.join(right_specie_names), ''.join(left_specie_names))
        else:
            reaction_name = 'R_%s_%s' % (''.join(left_specie_names), ''.join(right_specie_names))

        reactions.append (reaction_name)
        reaction_index = reactions.index (reaction_name)
        for specie, coeff in left_specie_coeff:
            if specie not in species:
                species.append (specie)
            specie_index = species.index (specie)
            if direction=='<':
                matrix[specie_index, reaction_index] = coeff
            else:
                matrix[specie_index, reaction_index] = -coeff
            
        for specie, coeff in right_specie_coeff:
            if specie not in species:
                species.append (specie)
            specie_index = species.index (specie)
            if direction=='<':
                matrix[specie_index, reaction_index] = -coeff
            else:
                matrix[specie_index, reaction_index] = coeff

        reactions_info[reaction_name]['reversible'] = reversible

    return matrix, species, reactions, species_info, reactions_info
