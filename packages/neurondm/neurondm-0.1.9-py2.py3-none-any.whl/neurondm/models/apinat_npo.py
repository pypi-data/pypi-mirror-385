import re
from collections import defaultdict
import rdflib
from pyontutils.sheets import Sheet
from pyontutils.namespaces import ilxtr, TEMP, rdfs, skos, owl
from neurondm.core import Config, NeuronEBM, Phenotype, EntailedPhenotype, log, OntId
from neurondm.models.apinat_pops_more import _genlabel


class NeuronApinatSimple(NeuronEBM):
    owlClass = ilxtr.NeuronApinatSimple
    shortname = 'apnsmp'


class AtN(Sheet):
    name = 'apinat-to-npo-sue'


sheet_classes = [
    type(f'AtN{sname.replace(" ", "_")}',
         (AtN,), dict(sheet_name=sname))
    for sname in (
            'aacar',
            'splen',
            'sstom',
            'sdcol',

            'bromo',
            'kblad',
            'bolew',
            'pancr',
    )]


def map_predicates(sheet_pred):
    p = {
        '': TEMP.BROKEN_EMPTY,
        'Soma-Location': ilxtr.hasSomaLocatedIn,
        'Axon-Terminal-Location': ilxtr.hasAxonPresynapticElementIn,
        'Axon-Leading-To-Sensory-Terminal': ilxtr.hasAxonLeadingToSensorySubcellularElementIn,
        'Axon-Location': ilxtr.hasAxonLocatedIn,
        'Dendrite-Location': ilxtr.hasDendriteLocatedIn,
        #'Dendrite-Terminal-Location': ilxtr.hasDendriteSensorySubcellularElementIn,
        'Forward-Connection': ilxtr.hasForwardConnectionPhenotype,
        'Axon-Sensory-Location': ilxtr.hasAxonSensorySubcellularElementIn,
        'Equivalent-To': owl.equivalentClass,
        'Functional-Circuit-Role': ilxtr.hasFunctionalCircuitRolePhenotype,
        'entail:hasInstanceInTaxon': ilxtr.hasInstanceInTaxon,
        'Organ-Destination': ilxtr.hasOrganTarget,
        'Has-Phenotype': ilxtr.hasPhenotype,  # needed for aacar 7 and 8
        'Projection-Phenotype': ilxtr.hasProjectionPhenotype,
    }[sheet_pred]
    return p


def main(debug=False):
    cs = [c() for c in sheet_classes]
    trips = [[cl] + [c.value for c in
                     (r.neuron_id(), r.exact_location(), r.location_id())]
             for cl in cs for r in cl.rows()
             if r.row_index > 0 and r.neuron_id().value
             and (not hasattr(r, 'exclude') or not r.exclude().value)]

    to_add = []
    dd = defaultdict(list)
    for c, _s, _p, _o in trips:
        for x in (_s, _p, _o):
            if re.match(r'(^[\s]+[^\s].*|.*[^\s][\s]+$)', x):
                msg = f'leading/trailing whitespace in {c} {_s!r} {_p!r} {_o!r}'
                log.error(msg)
                raise ValueError(msg)

        _s = _s.replace('/neuron-type-', '/apinat-simple/neuron-type-')
        s = OntId(_s)
        try:
            p = map_predicates(_p)
        except KeyError as e:
            log.error(f'sigh {s}')
            raise e

        if not _o:
            msg = f'object missing id for {OntId(s).curie} {OntId(p).curie}'
            if debug:
                log.warning(msg)
                _o = TEMP.BROKEN_EMPTY
            else:
                raise ValueError(msg)

        o = OntId(_o)

        if p == owl.equivalentClass or p == ilxtr.hasOrganTarget:
            to_add.append((s.u, p, o.u))
            continue

        try:
            if _p.startswith('entail:'):  # XXX FIXME hack
                dd[s].append(EntailedPhenotype(o, p))
            else:
                dd[s].append(Phenotype(o, p))
        except TypeError as e:
            log.error(f'bad data for {c} {s} {p} {o}')
            raise e

    problems = ('8a', '8v', 'sstom-6', 'keast-2', 'sdcol-k', 'sdcol-l')
    def eff(n):
        return bool([x for x in problems
                     if x in n.id_ and '20' not in n.id_])

    config = Config('apinat-simple-sheet')
    sigh = []
    nrns = []
    for id, phenos in dd.items():
        l, x = _genlabel(id)
        lab = 'simple ' + l
        to_add.append((id.u, rdfs.label, rdflib.Literal(lab)))
        n = NeuronApinatSimple(*phenos, id_=id)
        if eff(n):
            n._sigh()  # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX FIXME figure out why this is not getting called internally
            sigh.append(n)

        nrns.append(n)

    config.write()
    labels = (
        ilxtr.genLabel, ilxtr.localLabel, ilxtr.simpleLabel,
        ilxtr.simpleLocalLabel, rdfs.label, skos.prefLabel)
    to_remove = [t for t in config._written_graph if t[1] in labels]
    [config._written_graph.remove(t) for t in to_remove]
    [config._written_graph.add(t) for t in to_add]
    config._written_graph.namespace_manager.bind('apnsmp', str(ilxtr['apinat-simple/']))
    config._written_graph.write()
    config.write_python()
    return config,


if __name__ == '__main__':
    main()
