"""
molecularStructure.py
Contains class Molecule and class Atom.
"""
import copy

#Testing - replace "H" with "Br" to visualize all hydrogens
HYDROGEN = "H"

DEBUG = False # True

class Molecule(object):
    """
    This class represents the structure of a molecule.
        self.atoms :: [Atom].
    """

    def __init__(self, firstAtom):
        """
        firstAtom :: Atom.
        """
        self.atoms = [firstAtom]
    
    def addAtom(self, newAtom, targetAtom, bondOrder=1):
        """
        For adding new atoms to the molecule.

        newAtom :: Atom. The new atom to attach somewhere.
        targetAtom :: Atom. Must be in this molecule. Where newAtom attaches.
        bondOrder :: int. 1 for single, 2 for double, [...], 4 for quadruple.

        Throws error if targetAtom is not in the molecule.
        Throws error if bondOrder is invalid.
        """
        if bondOrder == 0:
            return
        if bondOrder not in [1, 2, 3, 4]:
            if DEBUG:
                raise StandardError("Invalid bond order: %s" % str(bondOrder))
        if targetAtom not in self.atoms:
            if DEBUG:
                raise StandardError("Target atom not already in molecule.")
        if newAtom in self.atoms:
            print "WARNING: new atom already in molecule. Using addBond."
            return self.addBond(targetAtom, newAtom, bondOrder)
        self.atoms.append(newAtom)
        self.addBond(newAtom, targetAtom, bondOrder)
        
    def addBond(self, atom1, atom2, bondOrder=1):
        """
        Creates a new bond between two atoms already in the molecule.
        atom1 :: Atom.
        atom2 :: Atom.
        bondOrder :: int. 1, 2, 3, or 4.
        """
        if atom1 not in self.atoms:
            if DEBUG:
                raise StandardError("Improper use of addBond")
            self.atoms.append(atom1)
        if atom2 not in self.atoms:
            if DEBUG:
                raise StandardError("Improper use of addBond")
            self.atoms.append(atom2)
        atom1.neighbors[atom2] = bondOrder
        atom2.neighbors[atom1] = bondOrder

    def addMolecule(self, molecule, foreignTarget, selfTarget, bondOrder=1):
        """
        Welds two molecules together by the given atoms.
        molecule :: Molecule.
        foreignTarget :: Atom. The atom on the other molecule.
        selfTarget :: Atom. An atom on this molecule.
        bondOrder :: int. Bond order for the new bond between foreignTarget
            and selfTarget.
        """
        #Preserves objects in added molecule (no deepcopy)
        for foreignAtom in molecule.atoms:
            if foreignAtom not in self.atoms:
                self.atoms.append(foreignAtom)
        self.addBond(selfTarget, foreignTarget, bondOrder)
        
    def removeAtom(self, target):
        """
        Remove an atom from this molecule. Destroys the atom.
        target :: Atom.
        """
        for atom in self.atoms:
            if target in atom.neighbors:
                del atom.neighbors[target]
        if target in self.atoms:
            self.atoms.remove(target)
        del target
        
    def changeBond(self, atom1, atom2, newBondOrder):
        """
        Changes the bond order of a bond.
        atom1 :: Atom.
        atom2 :: Atom.
        newBondOrder :: int. 0, 1, 2, 3, or 4.
        Note that newBondOrder=0 breaks the bond.
        """
        if DEBUG:
            assert atom1 in self.atoms, "Not in molecule: %s" % str(atom1)
            assert atom2 in self.atoms, "Not in molecule: %s" % str(atom2)

        if newBondOrder == 0:
            del atom1.neighbors[atom2]
            del atom2.neighbors[atom1]
        else:
            atom1.neighbors[atom2] = newBondOrder
            atom2.neighbors[atom1] = newBondOrder

    def addHydrogens(self):
        """
        Adds a full complement of hydrogens to every atom.
        """
        for atom in self.atoms:
            if atom.hcount == None:
                if atom.element == 'C':
                    maxval = 4
                elif atom.element in ['N', 'P']:
                    maxval = 3
                elif atom.element in ['O', 'S']:
                    maxval = 2
                elif atom.element in ['F', 'Br', 'Cl', 'I']:
                    maxval = 1
                else:
                    continue
                val = 0
                for neighbor in atom.neighbors:
                    if DEBUG:
                        assert neighbor in self.atoms
                    val += atom.neighbors[neighbor]
                diff = maxval - val

            else:
                hydrogen_already_added = 0
                for neighbor in atom.neighbors:
                    if neighbor.element == 'H':
                        hydrogen_already_added += 1
                diff = atom.hcount - hydrogen_already_added

            for _ in xrange(int(diff)):
                H = Atom(HYDROGEN)
                self.addAtom(H, atom, 1)

            ## TODO: If the atom is chiral, replace its chiral None with
            ## the relevant hydrogen

            for a in atom.neighbors:
                if a is None:
                    raise StandardError("None")

            if atom.chirality is not None:
                if atom.is_chiral and atom.chirality.hydrogen:
                    hydrogens = [a for a in atom.neighbors if a.element == 'H']
                    if DEBUG:
                        assert len(hydrogens) == 1, "Weird [C@H] misbehaviour"+\
                            " %s has %s h's" % (str(atom), str(len(hydrogens)))
                    hydrogen = hydrogens[0]
                    if atom.chiralA == None:
                        atom.chiralA = hydrogen
                    elif atom.chiralB == None:
                        atom.chiralB = hydrogen
                    elif atom.chiralC == None:
                        atom.chiralC = hydrogen
                    elif atom.chiralD == None:
                        atom.chiralD = hydrogen
                    else:
                        if DEBUG:
                            raise StandardError("[C@H] weirdness: why no H?")


    def countElement(self, element):
        """
        Counts the occurrences of `element` in this molecule's atoms.
        element :: str. Case matters.
        return :: int.
        """
        out = 0
        for atom in self.atoms:
            if atom.element == element:
                out += 1
        return out

    def removeBond(self, atom1, atom2):
        """
        Remove the bond between atom1 and atom2 without removing either
        from this molecule.
        atom1 :: Atom.
        atom2 :: Atom.
        """
        return self.changeBond(atom1, atom2, 0)

    def withHydrogens(self):
        """
        Return a version of this molecule in which explicit hydrogens have 
        been added to all molecules for which we can infer the number to add.
        """
        output = copy.deepcopy(self)
        output.addHydrogens()
        return output


class Atom(object):
    """
    This class represents the structure of a single atom. Not to be used alone;
    only really useful as a part of a Molecule.
        self.element :: str.
        self.charge :: int.
        self.neighbors :: {Atom, int}. This atom's neighbors; int -> bond order.

    Refer to moleculeToSmiles for these attributes; **ignore** them otherwise.
        self.flag :: int.
        self.rflag :: [(int, Atom)].
        self.nRead :: int.
        self.parent_atom :: 0 or Atom.
        self.nonHNeighbors = [Atom].
    """

    def sort_by(self):
        stuff = [str(k) + str(v) for k,v in self.neighbors.iteritems()]
        list.sort(stuff)
        return str(self) + str(stuff)

    def neighborElements(self):
        # :: set of strings
        return set([atom.element for atom in self.neighbors])

    def selectNeighborWithElement(self, element):
        # element :: string
        # :: a neighboring Atom
        for atom in self.neighbors:
            if atom.element == element:
                assert type(atom) is Atom
                return atom
        raise StandardError("No such neighboring atom: %s has no %s (instead has %s)" % (self.element, element, self.neighborElements()))
    
    def __str__(self):

        # Atoms are represented by the standard abbreviation of the chemical 
        # elements, in square brackets, such as [Au] for gold. Brackets can be 
        # omitted for the "organic subset" of B, C, N, O, P, S, F, Cl, Br, & I.
        # All other elements must be enclosed in brackets. If the brackets are
        # omitted, the proper number of implicit hydrogen atoms is assumed; for
        # instance the SMILES for water is simply O.

        # An atom holding one or more electrical charges is enclosed in 
        # brackets, followed by the symbol H if it is bonded to one or more
        # atoms of hydrogen, followed by the number of hydrogen atoms (as usual
        # one is omitted example: NH4 for ammonium), then by the sign '+'
        # for a positive charge or by '-' for a negative charge. The number of
        # charges is specified after the sign (except if there is one only);
        # however, it is also possible write the sign as many times as the ion
        # has charges: instead of "Ti+4", one can also write "Ti++++" (Titanium
        # IV, Ti4+). Thus, the hydroxide anion is represented by [OH-], the
        # oxonium cation is [OH3+] and the cobalt III cation (Co3+) is either
        # [Co+3] or [Co+++].

        ## ALL MOLECULES SHOULD HAVE HYDROGENS EXPLICITLY ATTACHED AS ATOMS

        output = self.element

        brackets = True
        # if self.hcount is None and not self.element == 'H' and \
        #     not ('H' in [i.element for i in self.neighbors]):
        #     brackets = False
        #     raise StandardError
        # else:
        #     brackets = True

        if not self.element in ['C','N','O','F','S','P','Cl','Br','I','B']:
            brackets = True

        ## Isotope
        if self.isotope is not None:
            brackets = True
            output = str(self.isotope) + output

        ## Chirality
        if self.is_chiral:
            brackets = True
            output = output + "@@"

            if self.hcount == 1:
                output += 'H'

        ## Hydrogens
        ## Since we represent hydrogens explicitly, as atoms OUTSIDE of this
        ## bracket structure -- which is valid -- we would never need to put
        ## them here.

        ## Charge
        if self.charge != 0 and self.charge is not None:
            brackets = True
            output = output + self.charge_string()

        ## Class
        if hasattr(self, 'clss'):
            brackets = True
            assert isinstance(self.clss, int)
            output += ':' + str(self.clss)

        if brackets:
            return '[%s]' % output
        else:
            return output

    def charge_string(self):
        "return :: str."
        if DEBUG:
            assert isinstance(self.charge, int)
        if self.charge == -1:
            return '-'
        elif self.charge < 0:
            return '-%s' % str(-self.charge)
        elif self.charge == +1:
            return '+'
        elif self.charge > 0:
            return '+%s' % str(self.charge)
        else:
            print "Warning: charge_string called when uncharged"
            return ""
    
    def __init__(self, element, charge=0):
        """
        Initialize. Charge, by default, is 0.
        element :: str.  Should be the periodic table abbreviation.
        charge :: int. Optional.
        """
        self.element = element
        self.charge = 0
        self.neighbors = dict()

        # Temporary values which should only be meaningful within smiles()
        # and subsmiles(), for traversing.
        self.flag = 0
        #for ring-finding
        self.rflag = [] #empty if not part of a ring bond
        self.n_read = 0 #neighbors already read
        self.parent_atom = 0 #atom right before this one
        self.non_h_neighbors = []

        self.is_aromatic = False
        self.isotope = None
        self.chirality = None
        self.hcount = None

        self.is_chiral = False
        self.chiralA = None
        self.chiralB = None
        self.chiralC = None
        self.chiralD = None

        self.is_cistrans = False
        self.CTotherC = None
        self.CTa = None
        self.CTb = None

    def newChiralCenter(self, reference, clockwiseList):
        """
        Set up this atom as a chiral center.
        reference :: Atom.
        clockwiseList :: a list of 3 Atoms.
        """
        # if self.is_chiral:
        #     print "Warning: Adding redundant chirality"
        self.is_chiral = True
        self.chiralA = reference
        self.chiralB, self.chiralC, self.chiralD = clockwiseList

    def chiralCWlist(self, reference):
        """
        Returns a list of the other 3 Atoms bonded to this Atom,
        in **clockwise** order when looking down `reference`.
        Note: Left-hand rule instead of right-hand rule.

        reference :: Atom.
        return :: a list of 3 Atoms.
        """
        if not self.is_chiral:
            if DEBUG:
                raise StandardError("%s atom is not chiral" % (str(self)))
        if reference is None:
            hydrogens = [atom for atom in self.neighbors if atom.element == 'H']
            assert len(hydrogens) > 0, "No hydrogen connected to this atom"
            reference = hydrogens[0]
        if reference is self.chiralA:
            return [self.chiralB, self.chiralC, self.chiralD]
        elif reference is self.chiralB:
            return [self.chiralA, self.chiralD, self.chiralC]
        elif reference is self.chiralC:
            return [self.chiralA, self.chiralB, self.chiralD]
        elif reference is self.chiralD:
            return [self.chiralA, self.chiralC, self.chiralB]
        else:
            msg = "Error in chiralCWlist: no such reference atom: %s\n" \
                % str(reference)
            msg += ", ".join([str(self.chiralA), str(self.chiralB),
                              str(self.chiralC), str(self.chiralD)])
            if DEBUG:
                raise StandardError(msg)
            else:
                return [atom for atom in self.neighbors if not atom == reference]
    
    def chiralRingList(self, inport, outpt):
        """
        Returns which substituent is up, followed by which one is down,
        in a ring context. Assume that the ring veers left (ccw).

        inport :: Atom.
        outpt :: Atom.
        return :: a tuple of 2 Atoms.

        **DEPRECATED**. Please stick to using chiralCWlist.
        """
        if not self.is_chiral:
            if DEBUG:
                raise StandardError("%s atom is not chiral" % (str(self)))
        if inport == self.chiralA:
            if outpt == self.chiralB:
                return (self.chiralC, self.chiralD)
            if outpt == self.chiralC:
                return (self.chiralD, self.chiralB)
            if outpt == self.chiralD:
                return (self.chiralB, self.chiralC)
        elif inport == self.chiralB:
            if outpt == self.chiralA:
                return (self.chiralD, self.chiralC)
            if outpt == self.chiralC:
                return (self.chiralA, self.chiralD)
            if outpt == self.chiralD:
                return (self.chiralC, self.chiralA)
        elif inport == self.chiralC:
            if outpt == self.chiralA:
                return (self.chiralB, self.chiralD)
            if outpt == self.chiralB:
                return (self.chiralD, self.chiralA)
            if outpt == self.chiralD:
                return (self.chiralA, self.chiralB)
        elif inport == self.chiralD:
            if outpt == self.chiralA:
                return (self.chiralC, self.chiralB)
            if outpt == self.chiralB:
                return (self.chiralA, self.chiralC)
            if outpt == self.chiralC:
                return (self.chiralB, self.chiralA)
                
        msg = "Error in chiralCWlist: no such inport and outpt: %s, %s\n" %\
              (str(inport), str(outpt))
        msg += ", ".join[str(self.chiralA), str(self.chiralB),
                         str(self.chiralC), str(self.chiralD)]
        if DEBUG:
            raise StandardError(msg)
        else:
            return [a for a in self.neighbors if not a == inport or a == outpt]
    
    def newCTCenter(self, otherC, a, b):
        """
        CTCenters (cis-trans centers) must come in pairs.  Both of the
        carbons across the double bond must have a CTCenter -- so you must
        execute this method once for each. Assuming that you're using the same
        plane of reference for each CT-center, this makes Atom a to be
        directly clockwise from otherC, and Atom b directly counterclockwise.

        otherC :: Atom.
        a :: Atom.
        b :: Atom.

        Raises AlleneError if newCTCenter has already been applied to this atom.
        """
        if self.is_cistrans and DEBUG:
            ## That would make this carbon the center of an allene!
            ## Keeping track of stereochem for allenes is Hard.
            ## TODO: Make it so that we can in fact handle allenes?
            raise AlleneError("Attempt to add extra CTcenter to %s" % str(self))
        if not (self.neighbors[otherC] == 2 and otherC.neighbors[self] == 2):
            if DEBUG:
                raise StandardError("cis-trans center without double bond")
            else:
                return
        self.CTotherC = otherC
        self.CTa = a
        self.CTb = b
    
    def eliminateChiral(self):
        """
        Destroys the chirality information.
        Don't worry, the atoms are still there.
        """
        if not self.is_chiral:
            print "Warning: Eliminating nonexistent chirality"
        self.chiralA = None
        self.chiralB = None
        self.chiralC = None
        self.chiralD = None
        self.is_chiral = False

    def eliminateCT(self):
        """
        Destroys the cis-trans information.
        Don't worry, the atoms are still there.
        """
        if not self.is_cistrans:
            print "Warning: Eliminating nonexistent cistrans"
        self.CTotherC = None
        self.CTa = None
        self.CTb = None
        self.is_cistrans = False

    def totalBondOrder(self):
        """
        Counts neighbors and returns the total bond order of this atom,
        not including implicit hydrogens.

        return :: int.
        """
        out = 0
        for neighbor in self.neighbors:
            out += self.neighbors[neighbor]
        return out

    def findAlkeneBond(self):
        """
        Returns the carbon atom to which this one is double-bonded, or None.

        return :: Atom or None.
        """
        for neighbor in self.neighbors:
            if self.neighbors[neighbor] == 2 and neighbor.element == 'C':
                return neighbor
        return None

class AlleneError(Exception):
    """
    Raised when we try to make an allene.  Tells higher functions that
    the reaction we just attempted should not be allowed.  (Even if it
    is technically chemically feasible.)
    """
    pass
