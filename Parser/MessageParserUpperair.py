from typing import IO

"""
    Represents a massage in PREPBUFR format.
    It's reponsible for parsing the message into LITTLER format.
"""
class MessageParserUpperair:
    allowed_types = ['ADPUPA','AIRCFT']

    left_pw_out = True

    # 31 fields (last one will be left out)
    headers = [""] * 31

    # Semifinal line, it is roughly the same 
    final_line = \
        "-777777.00000      0" + \
        "-777777.00000      0" + \
        "      1.00000      0" + \
        "-888888.00000      0" + \
        "-888888.00000      0" + \
        "-888888.00000      0" + \
        "-888888.00000      0" + \
        "-888888.00000      0" + \
        "-888888.00000      0" + \
        "-888888.00000      0"      

    # Last line, 
    verification_digits = "      1      0      0"

    @classmethod
    def valid_type(cls, msg_type) -> bool:
        return msg_type in cls.allowed_types

    @classmethod
    def valid_obs(cls, obs_qc: int) -> bool:
        return 0 <= obs_qc and obs_qc <= 3

    def __init__(self, msg_type: str, msg_subtype: int):
        if (msg_type not in self.allowed_types):
            raise ValueError("msg_type: {0} not in allowed_types: {1}.".format(msg_type, " ".join(allowed_types)))
        self.msg_type = msg_type

        if (self.msg_type == "ADPSFC"):
            if (msg_subtype == 181 or msg_subtype == 281 or msg_subtype == 183 or msg_subtype == 284):
                self.sub_type = "FM-12 SYNOP"
            elif (msg_subtype == 187 or msg_subtype == 287):
                self.sub_type = "FM-16 METAR"
            else:
                raise ValueError("ADPSFC : unexpected msg_subtype code: {}".format(msg_subtype))
        elif (self.msg_type == "SFCSHP"):
            if (msg_subtype == 180 or msg_subtype == 280 or msg_subtype == 183 or msg_subtype == 282 or msg_subtype == 284):
                self.sub_type = "FM-18 BUOY"
            elif (msg_subtype == 182):
                self.sub_type = "FM-13 SHIP"
            else:
                raise ValueError("SFCSHP : unexpected msg_subtype code: {}".format(msg_subtype))
        else:
            # Redundante: self.msg_type is in self.allowed_types
            raise ValueError("Unexpected msg_subtype code: {}".format(msg_type))

        self.observations = []
        

    ##############################################################
    # GENERAL INFORMATION (1ST LINE)
    ##############################################################
    def set_latitude(self, lat: float):
        # This field (F20.5) is MANDATORY
        content = "{:20.5f}".format(lat)
        self.headers[0] = content

    def set_longitude(self, long: float):
        # This field (F20.5) is MANDATORY
        content = "{:20.5f}".format(long)
        self.headers[1] = content

    def set_id(self,id: str):
        # This field (A40) is OPTIONAL
        content = " {:10s} get data information here.  ".format(id.decode())
        self.headers[2] = content

    def set_name(self):
        # This field (A40) is OPTIONAL
        content = "SURFACE DATA FROM ??????????? SOURCE    "
        self.headers[3] = content

    def set_platform(self):
        # This field (A40) is MANDATORY
        # Validations already done in constructor
        content = "{:40s}".format(self.sub_type)
        self.headers[4] = content

    def set_source(self):
        # This field (A40) is OPTIONAL
        content = "                                        " 
        self.headers[5] = content

    def set_elevation(self, elevation: float):
        # This field (F20.5) is MANDATORY (for some obs)
        content =  "{:20.5f}".format(elevation)
        self.headers[6] = content

    def set_valid_fields(self):
        # This field (I10) is UNUSED
        content = "         1"
        self.headers[7] = content

    def set_errors(self):
        # This field (I10) is UNUSED
        content = "         0"
        self.headers[8] = content

    def set_warnings(self):
        # This field (I10) is UNUSED
        content = "         0"
        self.headers[9] = content

    def set_sequence_number(self):
        # This field (I10) is OPTIONAL
        content = "         0"
        self.headers[10] = content

    def set_duplicates(self):
        # This field (I10) is UNUSED
        content = "         0"
        self.headers[11] = content

    def set_is_sounding(self):
        # This field (L10) is UNUSED
        content = "         T"
        self.headers[12] = content

    def set_bogus(self):
        # This field (L10) is OPTIONAL
        content = "         F"
        self.headers[13] = content

    def set_discard(self):
        # This field (L10) is OPTIONAL
        content = "         F"
        self.headers[14] = content

    def set_unix_time(self):
        # This field (I10) is OPTIONAL
        content = "   -888888"
        self.headers[15] = content

    def set_julian_day(self):
        # This field (I10) is OPTIONAL
        content = "   -888888"
        self.headers[16] = content

    def set_date_string(self, date_string: str):
        # This field (A20) is MANDATORY
        content = "      {:14s}".format(date_string)
        self.headers[17] = content

    def set_sea_level(self, sea_level: float = None):
        # This field (F13.5 + I7) is OPTIONAL
        content = ""
        if (sea_level is None):
            content = "-888888.00000      0"
        else:
            # O segundo parâmetro, um int, é o QC (quality control).
            # Até segunda ordem, vou inserir o default de zero.
            content = "{:13.5f}{:7d}".format(sea_level, 0)
        self.headers[18] = content

    def set_reference_pressure(self):
        # This field (F13.5 + I7) is MANDATORY (for some observations)
        content = "-888888.00000      0"
        self.headers[19] = content

    def set_ground_temperature(self):
        # This field (F13.5 + I7) is UNUSED
        content = "-888888.00000      0"
        self.headers[20] = content

    def set_sst(self):
        # This field (F13.5 + I7) is UNUSED
        content = "-888888.00000      0"
        self.headers[21] = content

    def set_psfc(self):
        # This field (F13.5 + I7) is OPTIONAL
        content = "-888888.00000      0"
        self.headers[22] = content

    def set_precipitation(self):
        # This field (F13.5 + I7) is UNUSED
        content = "-888888.00000      0"
        self.headers[23] = content

    def set_max_temp(self):
        # This field (F13.5 + I7) is UNUSED
        content = "-888888.00000      0"
        self.headers[24] = content

    def set_min_temp(self):
        # This field (F13.5 + I7) is UNUSED
        content = "-888888.00000      0"
        self.headers[25] = content

    def set_min_night_temp(self):
        # This field (F13.5 + I7) is UNUSED
        content = "-888888.00000      0"
        self.headers[26] = content

    def set_h3_pressure(self):
        # This field (F13.5 + I7) is UNUSED
        content = "-888888.00000      0"
        self.headers[27] = content

    def set_h24_pressure(self):
        # This field (F13.5 + I7) is UNUSED
        content = "-888888.00000      0"
        self.headers[28] = content

    def set_cloud_cover(self):
        # This field (F13.5 + I7) is OPTIONAL
        content = "-888888.00000      0"
        self.headers[29] = content

    def set_ceiling(self):
        # This field (F13.5 + I7) is UNUSED
        content = "-888888.00000      0"
        self.headers[30] = content

    def set_pw(self, pw = None):
        # This field (F13.5 + I7) is MANDATORY (for some observations)
        # For our usage, this field is left out completely
        # it is not saved in self.headers

        content = ""
        if (pw is None):
            content = "-888888.00000      0"
        else:
            content = "{:13.5f}{:7d}".format(pw, 0)
        
        if (not self.left_pw_out):
            self.headers[31] = left_pw_out


    ##############################################################
    # OBSERVATIONS (2ND LINE)
    ##############################################################
    def __set_obs(self, value: float, qc: int, idx_field: int, idx_level: int):
        # Default value
        content = "-888888.00000      0"

        if (idx_level >= len(self.observations)):
            self.observations.append([""] * 10)

        if (value is not None):
            if (qc is None):
                # Since there is no information about Quality Control
                # let's suppose it is a valid observation (qc = 0)
                qc = 0
            # If quality control fails, observation is discarded (default value)
            if (self.valid_obs(qc)):
                content = "{:13.5f}{:7d}".format(value, qc)
            else:
                print("quality control failure: qc = {}. This observation will be ignored.".format(qc))
        self.observations[idx_level][idx_field] = content

    def set_obs_pressure(self, idx: int, pressure: float = None, qc: int = None):
        if (pressure is None):
            self.__set_obs(pressure, qc, 0, idx)
        else:
            #Unit conversion: Hpa => Pa
            converted = pressure * 100
            self.__set_obs(converted, qc, 0, idx)

    def set_obs_height(self, idx: int, height: float = None, qc: int = None):
        self.__set_obs(height, qc, 1, idx)

    def set_obs_temperature(self, idx: int, temperature: float = None, qc: int = None):
        if (temperature is None):
            self.__set_obs(temperature, qc, 2, idx)
        else:
            # Unit conversion: oC => K
            converted = temperature + 273.15
            self.__set_obs(converted, qc, 2, idx)

    def set_obs_dew_point(self, idx: int, dew_point: float = None, qc = None):
        if (dew_point is None):
            self.__set_obs(dew_point, qc, 3, idx)
        else:
            # Unit conversion: oC => K
            converted = dew_point + 273.15
            self.__set_obs(converted, qc, 3, idx)

    def set_obs_wind_speed(self, idx: int, wind_speed = None, qc = None):
        self.__set_obs(wind_speed, qc, 4, idx)

    def set_obs_wind_direction(self, idx: int, wind_direction = None, qc = None):
        self.__set_obs(wind_direction, qc, 5, idx)

    def set_obs_wind_ew(self, idx: int, wind_ew = None, qc = None):
        self.__set_obs(wind_ew, qc, 6, idx)

    def set_obs_wind_ns(self, idx: int, wind_ns = None, qc = None):
        self.__set_obs(wind_ns, qc, 7, idx)

    def set_obs_relative_humidity(self, idx: int, relative_humidity = None, qc = None):
        self.__set_obs(relative_humidity, qc, 8, idx)

    def set_obs_thickness(self, idx: int, thickness = None, qc = None):
        self.__set_obs(thickness, qc, 9, idx)
    

    def full_message(self) -> str:
        lines = []

        if ("" in self.headers):
            raise Exception("A field in headers was not properly setted.")
        if ("" in self.observations):
            raise Exception("A field in observation was not properly setted.")

        header_line = "".join(self.headers)
        obs_line = "\n".join(["".join(obs_line) for obs_line in self.observations]) + "\n"

        lines.append(header_line)
        lines.append(obs_line)
        lines.append(self.final_line)
        lines.append(self.verification_digits)

        payload = "\n".join(lines) + "\n"
        return payload

    def dump_littler(self, file: IO):
        payload = self.full_message()
        file.write(payload.encode('ascii'))
