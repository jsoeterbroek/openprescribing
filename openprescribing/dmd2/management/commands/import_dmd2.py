import glob
import os
from lxml import etree

from openpyxl import load_workbook

from django.core.management import BaseCommand
from django.db import connection, transaction
from django.db.models import fields as django_fields

from dmd2 import models
from dmd2.models import AMP, AMPP, VMP, VMPP


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('dmd_data_path')
        parser.add_argument('mapping_path')

    def handle(self, *args, **kwargs):
        self.dmd_data_path = kwargs['dmd_data_path']
        self.mapping_path = kwargs['mapping_path']

        with transaction.atomic():
            self.import_dmd()
            self.import_bnf_code_mapping()
            self.set_vmp_bnf_codes()

    def import_dmd(self):
        # dm+d data is provided in several XML files:
        #
        # * f_amp2_3[ddmmyy].xml
        # * f_ampp2_3[ddmmyy].xml
        # * f_gtin2_0[ddmmyy].xml
        # * f_ingredient2_3[ddmmyy].xml
        # * f_lookup2_3[ddmmyy].xml
        # * f_vmp2_3[ddmmyy].xml
        # * f_vmpp2_3[ddmmyy].xml
        # * f_vtm2_3[ddmmyy].xml
        #
        # Each file contains a list or lists of elements that correspond to
        # instances of one of the models in models.py.
        #
        # Each such element has the structure:
        #
        # <OBJ_TYPE>
        #   <FIELD1>value</FIELD1>
        #   <FIELD2>value</FIELD2>
        #   <FIELD3>value</FIELD3>
        # </OBJ_TYPE>
        #
        # These elements are arranged differently in different files.
        #
        # The ingredient and VTM files just contain a list of elements
        # corresponding to instances of Ing and VTM respectively.  For
        # instance:
        #
        # <INGREDIENT_SUBSTANCES>
        #     <!-- Generated by NHSBSA PPD -->
        #     <ING>...</ING>
        #     <ING>...</ING>
        #     ...
        # </INGREDIENT_SUBSTANCES>
        #
        # The VMP, VMPP, AMP, AMPP and lookup files contain several lists of
        # elements, corresponding to multiple types of objects.  For instance:
        #
        # <VIRTUAL_MED_PRODUCTS>
        #     <!-- Generated by NHSBSA PPD -->
        #     <VMPS>
        #         <VMP>...</VMP>
        #         <VMP>...</VMP>
        #         ...
        #     </VMPS>
        #     <VIRTUAL_PRODUCT_INGREDIENT>
        #         <VPI>...</VPI>
        #         <VPI>...</VPI>
        #         ...
        #     </VIRTUAL_PRODUCT_INGREDIENT>
        #     <ONT_DRUG_FORM>
        #         <ONT>...</ONT>
        #         <ONT>...</ONT>
        #         ...
        #     </ONT_DRUG_FORM>
        #     ...
        # <VIRTUAL_MED_PRODUCTS>
        #
        # The GTIN file is a bit weird and the data requires a little massaging
        # before it can be imported.  See code below.
        #
        # Since the data model contains foreign key constraints, the order we
        # import the files is significant.
        #
        # When importing the data, we first delete all existing instances,
        # because the IDs of some SNOMED objects can change.

        # lookup
        for elts in self.load_elts('lookup'):
            model_name = self.make_model_name(elts.tag)
            model = getattr(models, model_name)
            self.import_model(model, elts)

        # ingredient
        elts = self.load_elts('ingredient')
        self.import_model(models.Ing, elts)

        # vtm
        elts = self.load_elts('vtm')
        self.import_model(models.VTM, elts)

        # vmp
        for elts in self.load_elts('vmp'):
            model_name = self.make_model_name(elts[0].tag)
            model = getattr(models, model_name)
            self.import_model(model, elts)

        # vmpp
        for elts in self.load_elts('vmpp'):
            if elts[0].tag == 'CCONTENT':
                # TODO Handle CCONTENT
                continue

            model_name = self.make_model_name(elts[0].tag)
            model = getattr(models, model_name)
            self.import_model(model, elts)

        # amp
        for elts in self.load_elts('amp'):
            if len(elts) == 0:
                # For test data, some lists of elements are empty (eg
                # AP_INFORMATION), and so we can't look at the first element of
                # the list to get the name of the corresponding model.
                continue

            model_name = self.make_model_name(elts[0].tag)
            model = getattr(models, model_name)
            self.import_model(model, elts)

        # ampp
        for elts in self.load_elts('ampp'):
            if len(elts) == 0:
                # For test data, some lists of elements are empty (eg
                # APPLIANCE_PACK_INFO), and so we can't look at the first
                # element of the list to get the name of the corresponding
                # model.
                continue

            if elts[0].tag == 'CCONTENT':
                # TODO Handle CCONTENT
                continue

            model_name = self.make_model_name(elts[0].tag)
            model = getattr(models, model_name)
            self.import_model(model, elts)

        # gtin
        elts = self.load_elts('gtin')[0]
        for elt in elts:
            assert elt[0].tag == 'AMPPID'
            assert elt[1].tag == 'GTINDATA'

            elt[0].tag = 'APPID'
            for gtinelt in elt[1]:
                elt.append(gtinelt)
            elt.remove(elt[1])
        self.import_model(models.GTIN, elts)

    def load_elts(self, filename_fragment):
        '''Return list of non-comment top-level elements in given file.'''

        paths = glob.glob(os.path.join(self.dmd_data_path, 'f_{}2_*.xml'.format(filename_fragment)))
        assert len(paths) == 1

        with open(paths[0]) as f:
            doc = etree.parse(f)

        root = doc.getroot()
        elts = list(root)
        assert isinstance(elts[0], etree._Comment)
        return elts[1:]

    def import_model(self, model, elts):
        '''Import model instances from list of XML elements.'''

        model.objects.all().delete()

        boolean_field_names = [
            f.name for f in model._meta.fields
            if isinstance(f, django_fields.BooleanField)
        ]

        table_name = model._meta.db_table
        column_names = [
            f.db_column or f.name
            for f in model._meta.fields
            if not isinstance(f, django_fields.AutoField)
        ]
        sql = 'INSERT INTO {} ({}) VALUES ({})'.format(
            table_name,
            ', '.join(column_names),
            ', '.join(['%s'] * len(column_names))
        )

        values = []

        for elt in elts:
            row = {}

            for field_elt in elt:
                name = field_elt.tag.lower()
                if name == 'desc':
                    # "desc" is a really unhelpful field name if you're writing
                    # SQL!
                    name = 'descr'
                elif name == 'dnd':
                    # For consistency with the rest of the data, we rename
                    # "dnd" to "dndcd", as it is a foreign key field.
                    name = 'dndcd'

                value = field_elt.text
                row[name] = value

            for name in boolean_field_names:
                row[name] = (name in row)

            values.append([row.get(name) for name in column_names])

        with connection.cursor() as cursor:
            cursor.executemany(sql, values)

    def make_model_name(self, tag_name):
        '''Construct name of Django model from XML tag name.'''

        if tag_name in [
            'VTM',
            'VPI',
            'VMP',
            'VMPP',
            'AMP',
            'AMPP',
            'GTIN',
        ]:
            return tag_name
        else:
            return ''.join(tok.title() for tok in tag_name.split('_'))

    def import_bnf_code_mapping(self):
        type_to_model = {
            ('Presentation', 'VMP'): VMP,
            ('Presentation', 'AMP'): AMP,
            ('Pack', 'VMP'): VMPP,
            ('Pack', 'AMP'): AMPP,
        }

        wb = load_workbook(filename=self.mapping_path)
        rows = wb.active.rows

        headers = next(rows)
        assert headers[0].value == 'Presentation / Pack Level'
        assert headers[1].value == 'VMP / AMP'
        assert headers[2].value == 'BNF Code'
        assert headers[4].value == 'SNOMED Code'

        VMP.objects.update(bnf_code=None)
        AMP.objects.update(bnf_code=None)
        VMPP.objects.update(bnf_code=None)
        AMPP.objects.update(bnf_code=None)

        for ix, row in enumerate(rows):
            model = type_to_model[(row[0].value, row[1].value)]

            bnf_code = row[2].value
            snomed_id = row[4].value

            if bnf_code is None or snomed_id is None:
                continue

            if bnf_code == "'" or snomed_id == "'":
                continue

            bnf_code = bnf_code.lstrip("'")
            snomed_id = snomed_id.lstrip("'")

            try:
                obj = model.objects.get(id=snomed_id)
            except model.DoesNotExist:
                # TODO: log this
                continue
            obj.bnf_code = bnf_code
            obj.save()

    def set_vmp_bnf_codes(self):
        '''There are many VMPs that do not have BNF codes set in the mapping,
        but whose VMPPs all have the same BNF code.  In these cases, we think
        that the VMPPs' BNF code can be applied to the VMP too.
        '''

        vmps = VMP.objects.filter(
            bnf_code__isnull=True
        ).prefetch_related('vmpp_set')

        # TODO: log all these

        for vmp in vmps:
            vmpp_bnf_codes = {
                vmpp.bnf_code
                for vmpp in vmp.vmpp_set.all()
                if vmpp.bnf_code
            }

            if len(vmpp_bnf_codes) == 1:
                vmp.bnf_code = list(vmpp_bnf_codes)[0]
                vmp.save()
