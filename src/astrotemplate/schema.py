# Schema for the SIMPLE database

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Enum, DateTime, ForeignKeyConstraint
import enum
from astrodbkit2.astrodb import Base
from sqlalchemy.orm import Mapped

# todo: make "tabulardata" or "physicaldata" abstract classes.
# -------------------------------------------------------------------------------------------------------------------
# Reference tables
class Publications(Base):
    """ORM for publications table.
    This stores reference information (DOI, bibcodes, etc) and has shortname as the primary key
    """
    __tablename__ = 'Publications'
    reference = Column(String(30), primary_key=True, nullable=False)
    bibcode = Column(String(100))
    doi = Column(String(100))
    description = Column(String(1000))


class Telescopes(Base):
    __tablename__ = 'Telescopes'
    telescope = Column(String(30), primary_key=True, nullable=False)
    description = Column(String(1000))
    reference = Column(String(30), ForeignKey('Publications.reference', onupdate='cascade'))


class Instruments(Base):
    __tablename__ = 'Instruments'
    instrument = Column(String(30), primary_key=True, nullable=False)
    description = Column(String(1000))
    reference = Column(String(30), ForeignKey('Publications.reference', onupdate='cascade'))

# instead of having modes...telescope --> instrument --> mode (used mostly for spectra). think about SVO.
class Modes(Base):
    __tablename__ = 'Modes'
    mode = Column(String(30), primary_key=True, nullable=False)
    instrument = Column(String(30), ForeignKey('Instruments.instrument', onupdate='cascade'), primary_key=True)
    telescope = Column(String(30), ForeignKey('Telescopes.telescope', onupdate='cascade'), primary_key=True)
    description = Column(String(1000))


class PhotometryFilters(Base):
    """
    ORM for filter table.
    This stores relationships between filters and instruments, telescopes, as well as wavelength and width
    """
    __tablename__ = 'PhotometryFilters'
    band = Column(String(30), primary_key=True, nullable=False)  # of the form instrument.filter (see SVO)
    instrument = Column(String(30), ForeignKey('Instruments.instrument', onupdate='cascade'), primary_key=True)
    telescope = Column(String(30), ForeignKey('Telescopes.telescope', onupdate='cascade'), primary_key=True)
    effective_wavelength = Column(Float, nullable=False)
    width = Column(Float)


class Versions(Base):
    """
    ORM for Versions table
    This stores the version numbers for the database
    """
    __tablename__ = 'Versions'
    version = Column(String(30), primary_key=True, nullable=False)
    start_date = Column(String(30))
    end_date = Column(String(30))
    description = Column(String(1000))


# -------------------------------------------------------------------------------------------------------------------
# Hard-coded enumerations

class Regime(enum.Enum):
    """Enumeration for spectral type, spectra, and photometry regimes
    Use UCD controlled vocabulary: https://www.ivoa.net/documents/UCD1+/20200212/PEN-UCDlist-1.4-20200212.html#tth_sEcB
    The string values are used, not the variable names.
    """
    ultraviolet = 'em.UV'
    optical_UCD = 'em.opt'
    optical = 'optical'
    nir_UCD = 'em.IR.NIR'  # Near-Infrared, 1-5 microns
    nir = 'nir'
    infrared = 'em.IR'  # Infrared part of the spectrum
    mir_UCD = 'em.IR.MIR'  # Medium-Infrared, 5-30 microns
    mir = 'mir'
    millimeter = 'em.mm'
    radio = 'em.radio'
    unknown = 'unknown'

# -------------------------------------------------------------------------------------------------------------------
# Main tables
class Sources(Base):
    """ORM for the sources table. This stores the main identifiers for our objects along with ra and dec"""
    __tablename__ = 'Sources'
    source = Column(String(100), primary_key=True, nullable=False)
    ra = Column(Float)
    dec = Column(Float)
    epoch = Column(Float)  # decimal year
    equinox = Column(String(10))  # eg, J2000
    shortname = Column(String(30))  # not needed?
    reference = Column(String(30), ForeignKey('Publications.reference', onupdate='cascade'), nullable=False)
    other_references = Column(String(100))
    comments = Column(String(1000))


class Names(Base):
    __tablename__ = 'Names'
    source = Column(String(100), ForeignKey('Sources.source', ondelete='cascade', onupdate='cascade'),
                    nullable=False, primary_key=True)
    other_name = Column(String(100), primary_key=True, nullable=False)

# todo: make "tabulardata" or "physicaldata" abstract classes.

class _DataPointerTable:
    # __tablename__ = 'DataPointerTable'
    # source = Column(String(100),
    #                 nullable=False, primary_key=True)
    data = Column(String(100))
    comments = Column(String(1000))
    data_type = Column(String(32), nullable=False)
    # Other columns common to all child tables

class Spectra(_DataPointerTable, Base):
    __tablename__ = 'Spectra'
    source = Column(String(100), ForeignKey('Sources.source', ondelete='cascade', onupdate='cascade'),
                    nullable=False, primary_key=True)
    reference = Column(String(30), ForeignKey('Publications.reference', ondelete='cascade', onupdate='cascade'),
                       primary_key=True)
    # Data
    spectrum = Column(String(1000), nullable=False)  # URL of spectrum location
    original_spectrum = Column(String(1000))  # URL of original spectrum location, if applicable
    local_spectrum = Column(String(1000))  # local directory (via environment variable) of spectrum location
    # onupdate = 'cascade'), primary_key = True
    # Metadata
    # regime = Column(Enum(Regime, create_constraint=True, values_callable=lambda x: [e.value for e in x],
    #                      native_enum=False),
    #                 )  # eg, Optical, Infrared, etc
    telescope = Column(String(30), ForeignKey('Telescopes.telescope'), onupdate='cascade',primary_key=True)
    instrument = Column(String(30), ForeignKey('Instruments.instrument'), onupdate='cascade',primary_key=True)
    mode = Column(String(30))  # eg, Prism, Echelle, etc
    observation_date = Column(DateTime)
    wavelength_units = Column(String(20))
    flux_units = Column(String(20))
    wavelength_order = Column(Integer)
    other_references = Column(String(100))

