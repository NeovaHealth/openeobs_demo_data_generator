# pylint: disable=C0103
"""Generates NEWS Observations"""
from xml.etree.ElementTree import Element, SubElement, Comment


class NewsGenerator(object):
    """Generates NEWS Observations"""
    def __init__(self, ward_strategy):

        # Create root element
        self.root = Element('openerp')

        # Create data inside root element
        self.data = SubElement(self.root, 'data', {'noupdate': '1'})

        self.minutes = {
            'high': 30, 'medium': 60, 'low': 240, 'none': 720
        }
        self.values = {
            'high': {
                'respiration_rate': '15',
                'indirect_oxymetry_spo2': '94',
                'oxygen_administration_flag': 'True',
                'body_temperature': '40.5',
                'blood_pressure_systolic': '120',
                'blood_pressure_diastolic': '80',
                'pulse_rate': '65',
                'avpu_text': 'V'
            },
            'medium': {
                'respiration_rate': '15',
                'indirect_oxymetry_spo2': '95',
                'oxygen_administration_flag': 'False',
                'body_temperature': '40.5',
                'blood_pressure_systolic': '120',
                'blood_pressure_diastolic': '80',
                'pulse_rate': '65',
                'avpu_text': 'A'
            },
            'low': {
                'respiration_rate': '15',
                'indirect_oxymetry_spo2': '99',
                'oxygen_administration_flag': 'False',
                'body_temperature': '40.5',
                'blood_pressure_systolic': '120',
                'blood_pressure_diastolic': '80',
                'pulse_rate': '65',
                'avpu_text': 'A'
            },
            'none': {
                'respiration_rate': '15',
                'indirect_oxymetry_spo2': '99',
                'oxygen_administration_flag': 'False',
                'body_temperature': '37.5',
                'blood_pressure_systolic': '120',
                'blood_pressure_diastolic': '80',
                'pulse_rate': '65',
                'avpu_text': 'A'
            }
        }

        # Generate the patient observations
        self.generate_news(ward_strategy)

    def generate_news(self, ward_strategy):
        """
        Read the patients in the document and generate NEWS observations for
        them until the schedule date reaches 'now' or later
        :return:
        """
        for patient in ward_strategy.patients:
            risk = self.get_risk(ward_strategy)
            print 'generating news for ' + patient.patient_id + ' with risk ' \
                  + risk
            offset_position = patient.date_terminated.find('timedelta(-') + 11
            offset = int(patient.date_terminated[offset_position])
            minutes = 60
            sequence = 0
            schedule_date_eval = '(datetime.now() + timedelta(-{0})' \
                                 ' + timedelta(minutes={1}))' \
                                 '.strftime(\'%Y-%m-%d %H:%M:%S\')'
            schedule_date_eval = schedule_date_eval.format(offset, minutes)
            # Generate observation data
            while self.to_be_completed(offset, minutes):
                print 'generating ' + str(sequence) + ' news for ' + \
                      patient.patient_id
                self.generate_completed_news_data(
                    patient, schedule_date_eval, risk, sequence)
                minutes += self.minutes[risk]
                patient.date_terminated = schedule_date_eval
                sequence += 1
                schedule_date_eval = schedule_date_eval.format(offset, minutes)
            self.generate_scheduled_news_data(
                patient, schedule_date_eval, sequence)

    def to_be_completed(self, offset, minutes):
        return float(minutes)/(24*60) < offset

    def get_risk(self, ward_strategy):
        for key in ward_strategy.risk_distribution.keys():
            if ward_strategy.risk_distribution[key]:
                ward_strategy.risk_distribution[
                    key] = ward_strategy.risk_distribution[key] - 1
                return key
        return False

    def generate_completed_news_data(
            self, patient, schedule_date, risk, sequence):
        self.data.append(
            Comment(
                'NEWS data for patient {0}'.format(patient.patient_id)
            )
        )
        self.create_activity_news_record(
            patient, schedule_date, 'completed', sequence)
        self.create_news_record(patient, risk, sequence)
        self.update_activity_news(patient, sequence)

    def generate_scheduled_news_data(self, patient, schedule_date, sequence):
        self.data.append(
            Comment(
                'NEWS data for patient {0}'.format(patient.patient_id)
            )
        )
        self.create_activity_news_record(
            patient, schedule_date, 'scheduled', sequence)
        self.create_news_record(patient, 'partial', sequence)
        self.update_activity_news(patient, sequence)

    def update_activity_news(self, patient, sequence):
        """Update activity NEWS"""

        # Create nh.clinical.patient.observation.ews record with id & data
        update_activity_news_record = SubElement(
            self.data,
            'record',
            {
                'model': 'nh.activity',
                'id': 'nhc_activity_demo_news_{0}_{1}'.format(
                    patient.id, sequence)
            }
        )

        # Create activity ref
        eval_string = '\'nh.clinical.patient.observation.ews,\' + ' \
                      'str(ref(\'nhc_demo_news_{0}_{1}\'))'
        SubElement(
            update_activity_news_record,
            'field',
            {
                'name': 'data_ref',
                'eval': eval_string.format(patient.id, sequence)
            }
        )

    def create_news_record(self, patient, risk, sequence):
        """Create NEWS record"""

        # Create nh.activity NEWS record with id
        news_record = SubElement(
            self.data,
            'record',
            {
                'model': 'nh.clinical.patient.observation.ews',
                'id': 'nhc_demo_news_{0}_{1}'.format(
                    patient.id, sequence)
            }
        )

        # Create activity_id reference
        SubElement(
            news_record,
            'field',
            {
                'name': 'activity_id',
                'ref': 'nhc_activity_demo_news_{0}_{1}'.format(
                    patient.id, sequence)
            }
        )

        # Create patient_id reference
        SubElement(
            news_record,
            'field',
            {
                'name': 'patient_id',
                'ref': 'nh_clinical.' + patient.patient_id
            }
        )

        # Create observation data
        if risk != 'partial':
            SubElement(
                news_record,
                'field',
                {
                    'name': 'respiration_rate',
                    'eval': self.values[risk]['respiration_rate']
                }
            )
            SubElement(
                news_record,
                'field',
                {
                    'name': 'indirect_oxymetry_spo2',
                    'eval': self.values[risk]['indirect_oxymetry_spo2']
                }
            )
            SubElement(
                news_record,
                'field',
                {
                    'name': 'oxygen_administration_flag',
                    'eval': self.values[risk]['oxygen_administration_flag']
                }
            )
            SubElement(
                news_record,
                'field',
                {
                    'name': 'body_temperature',
                    'eval': self.values[risk]['body_temperature']
                }
            )
            SubElement(
                news_record,
                'field',
                {
                    'name': 'blood_pressure_systolic',
                    'eval': self.values[risk]['blood_pressure_systolic']
                }
            )
            SubElement(
                news_record,
                'field',
                {
                    'name': 'blood_pressure_diastolic',
                    'eval': self.values[risk]['blood_pressure_diastolic']
                }
            )
            SubElement(
                news_record,
                'field',
                {
                    'name': 'pulse_rate',
                    'eval': self.values[risk]['pulse_rate']
                }
            )
            avpu = SubElement(
                news_record,
                'field',
                {
                    'name': 'avpu_text',
                }
            )
            avpu.text = self.values[risk]['avpu_text']

    def create_activity_news_record(self, patient, date, state, sequence):
        """Create activity NEWS record"""

        # Create nh.activity NEWS record with id
        activity_news_record = SubElement(
            self.data,
            'record',
            {
                'model': 'nh.activity',
                'id': 'nhc_activity_demo_news_{0}_{1}'.format(
                    patient.id, sequence)
            }
        )

        # Create patient_id reference
        SubElement(
            activity_news_record,
            'field',
            {
                'name': 'patient_id',
                'ref': 'nh_clinical.' + patient.patient_id
            }
        )

        # Create creator_id reference
        SubElement(
            activity_news_record,
            'field',
            {
                'name': 'creator_id',
                'ref': 'nh_clinical.' + patient.placement_id
            }
        )

        # Create parent_id reference
        SubElement(
            activity_news_record,
            'field',
            {
                'name': 'parent_id',
                'ref': 'nh_clinical.' + patient.spell_activity_id
            }
        )

        # Create spell_activity_id reference
        SubElement(
            activity_news_record,
            'field',
            {
                'name': 'spell_activity_id',
                'ref': 'nh_clinical.' + patient.spell_activity_id
            }
        )

        # Create activity state
        activity_admit_state = SubElement(activity_news_record,
                                          'field',
                                          {'name': 'state'})
        activity_admit_state.text = state

        # Create activity data model
        activity_admit_model = SubElement(activity_news_record,
                                          'field',
                                          {'name': 'data_model'})
        activity_admit_model.text = 'nh.clinical.patient.observation.ews'

        # Create location_id reference
        SubElement(
            activity_news_record,
            'field',
            {
                'name': 'location_id',
                'ref': 'nh_clinical.' + patient.location_id
            }
        )

        # Create activity date terminated
        SubElement(
            activity_news_record,
            'field',
            {
                'name': 'date_scheduled',
                'eval': date
            }
        )

        # Create activity date scheduled
        if state == 'completed':
            SubElement(
                activity_news_record,
                'field',
                {
                    'name': 'date_terminated',
                    'eval': date
                }
            )