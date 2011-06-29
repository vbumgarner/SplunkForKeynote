import xml.sax
import sys
import csv
from csvUpdater import CsvUpdater

try:
    set
except NameError:
    from sets import Set as set

class KeynoteHandler(xml.sax.ContentHandler):
    def __init__(self, filename):
        self.agent_meta_data = []

        self.slot_meta_data = []

        self.current_slot_attrs = {}

        self.current_measurement = {}

        self.current_page = {}

        self.current_request = {}

        self.current_detail = None

        self.keys_to_skip = ["datetime"]

        self.filename = filename

    def get_date(self):
        return self.current_measurement["datetime"]
        
    def build_attrs_string(self, d):
        s = ""
        for k,v in d.items():
            if k not in self.keys_to_skip:
                s += ' ' + k + '="' + v + '"'
        return s

    def build_filename_string(self):
        fn = {}
        fn["filename"] = self.filename
        return self.build_attrs_string( fn )

    def write_summary( self, attrs ):
        print self.get_date() + " st=summary" + self.build_attrs_string( self.current_measurement ) + self.build_attrs_string( attrs ) + self.build_filename_string()
#        print "write_summary!"
#        

    def write_detail(self):
        print self.get_date() + " st=detail" + self.build_attrs_string( self.current_measurement ) + self.build_attrs_string( self.current_detail ) + self.build_attrs_string( self.current_page ) + self.build_filename_string()
#       print "write_detail!"
#        self.current_measurement, self.current_detail

    def write_page_performance(self):
        print self.get_date() + " st=page" + self.build_attrs_string( self.current_measurement ) + self.build_attrs_string( self.current_page ) + self.build_filename_string()
#        print "write_page_performance!"
#        self.current_measurement, self.current_page

    def write_agent_meta(self):
        csvUpdater = CsvUpdater(os.path.normcase('../lookups/agent_meta_data.csv'),['instance_id'])
        csvUpdater.commit(self.agent_meta_data)

    def write_slot_meta(self):
        csvUpdater = CsvUpdater(os.path.normcase('../lookups/slot_meta_data.csv'),['page_seq','slot_id'])
        csvUpdater.commit(self.slot_meta_data)



    def startElement(self, name, attrs):
        if name == "AGENT_META_DATA":
            agent = {}
            agent.update(attrs)
            self.agent_meta_data.append(agent)
        if name == "SLOT_META_DATA":
            self.current_slot_attrs = attrs
        if name == "PAGE_META_DATA":
            current_page = {}
            current_page.update(self.current_slot_attrs)
            current_page.update(attrs)
            self.slot_meta_data.append(current_page)

        if name == "TXN_MEASUREMENT":
#            this_agent = self.agent_meta_data[attrs["agent"] + "-" + attrs["agent_inst"]]
#            this_slot = self.slot_meta_data[attrs["slot"]]
            self.current_measurement.update(attrs)
        if name == "TXN_SUMMARY":
            self.write_summary(attrs)
        if name == "TXN_PAGE":
            self.current_page = {}
            self.current_page["seq"] = attrs["page_seq"]
        if ( ( name == "TXN_PAGE_PERFORMANCE" ) or ( name == "TXN_PAGE_OBJECT" ) or ( name == "TXN_PAGE_STATUS" ) ):
            self.current_page.update(attrs)
        if ( ( name == "TXN_BASE_PAGE" ) or ( name == "TXN_REDIRECT" ) or ( name == "TXN_PAGE_ELEMENT" ) ):
            self.current_detail = {}
            self.current_detail.update(attrs)
        if ( name == "TXN_DETAIL_PERFORMANCE" or name == "TXN_DETAIL_OBJECT" or name == "TXN_DETAIL_STATUS" ):
            self.current_detail.update(attrs)
            if ( ("object_text" in attrs) and ("url" not in self.current_page ) ):
                self.current_page["url"] = attrs["conn_string_text"] + attrs["object_text"]
            
    def endElement(self, name):
        if name == "TXN_PAGE":
            self.write_detail()
            self.write_page_performance()
        if ( ( name == "TXN_BASE_PAGE" ) or ( name == "TXN_REDIRECT" ) or ( name == "TXN_PAGE_ELEMENT" ) ):
            self.write_detail()


class KeynoteParser():

    def parse_file(self, f ):
        self.parse_fh(open( f ,"r") , file.name)

    def parse_fh(self, fh, filename="unknown" ):
#        sys.stderr.write("Hello from parse_fh \n")
        handler = KeynoteHandler( filename )

        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse( fh )

        handler.write_agent_meta()
        handler.write_slot_meta()



'''
<TXN_DATA_FEED>
  <TXN_META_DATA agreement_id="170968">
    <AGENT_META_DATA agent_id="40157" instance_id="40158" country="USA" description="HF Transaction San Francisco Sprint" region="West" ip="205.163.212.24" backbone="Sprint" weight="1" city="San Francisco"/>
    <SLOT_META_DATA slot_id="911844" slot_alias="DEMO Site - Multi-page Transaction with Virtual Pages" pages="6" subservice="TXP">
      <PAGE_META_DATA page_url="http://scdemo01.keynote.com/site/" page_alias="SC Demo Home" page_seq="1"/>
    </SLOT_META_DATA>
  </TXN_META_DATA>

  <DP_TXN_MEASUREMENTS>
    <TXN_MEASUREMENT agent="42627" slot="911845" datetime="2010-NOV-17 06:24:56" target="1114353" agent_inst="46505" profile="0">
      <TXN_SUMMARY delta_msec="1567" element_count="91" trans_level_comp_msec="0" estimated_cache_delta_msec="1316" content_errors="0" delta_user_msec="3393" resp_bytes="325159"/>
      <TXN_PAGE page_seq="3">
        <TXN_PAGE_PERFORMANCE delta_msec="80" first_byte_msec="16" delta_user_msec="339" remain_packets_delta="3" first_packet_delta="56" system_delta="0" request_delta="0" start_msec="2614" estimated_cache_delta_msec="80"/>
        <TXN_PAGE_OBJECT redir_count="1" element_count="2" page_bytes="6406" redir_delta="19"/>
        <TXN_PAGE_STATUS content_errors="0"/>
        <TXN_PAGE_DETAILS page="3">
          <TXN_BASE_PAGE record_seq="1">
            <TXN_DETAIL_PERFORMANCE first_packet_delta="56" system_delta="0" request_delta="0" start_msec="20" element_delta="78" remain_packets_delta="3"/>
            <TXN_DETAIL_OBJECT msmt_conn_id="1348" element_cached="0" request_bytes="977" conn_string_text="http://scdemo01.keynote.com" content_type="51" header_bytes="439" ip_address="97.107.129.30" object_text="/shop/index.php?route=account/login" content_bytes="5120"/>
            <TXN_DETAIL_STATUS status_code="200"/>
          </TXN_BASE_PAGE>
          <TXN_REDIRECT record_seq="1" record_subseq="1">
            <TXN_DETAIL_PERFORMANCE first_packet_delta="19" system_delta="0" request_delta="0" start_msec="0" element_delta="19" remain_packets_delta="0"/>
            <TXN_DETAIL_OBJECT msmt_conn_id="1484" element_cached="0" request_bytes="981" conn_string_text="http://scdemo01.keynote.com" content_type="51" header_bytes="499" ip_address="97.107.129.30" object_text="/shop/index.php?route=checkout/shipping" content_bytes="20"/>
            <TXN_DETAIL_STATUS status_code="302"/>
          </TXN_REDIRECT>
          <TXN_PAGE_ELEMENT record_seq="9">
            <TXN_DETAIL_PERFORMANCE first_packet_delta="1" system_delta="0" request_delta="0" start_msec="337" element_delta="2" remain_packets_delta="1"/>
            <TXN_DETAIL_OBJECT msmt_conn_id="1600" element_cached="0" request_bytes="880" conn_string_text="http://www.google-analytics.com" content_type="38" header_bytes="293" ip_address="173.194.33.100" object_text="/__utm.gif?utmwv=4.8.6&amp;utmn=1851771348&amp;utmhn=scdemo01.keynote.com&amp;utmcs=utf-8&amp;utmsr=1024x768&amp;utmsc=32-bit&amp;utmul=en-us&amp;utmje=1&amp;utmfl=10.0%20r42&amp;utmdt=Account%20Login&amp;utmhid=1646102387&amp;utmr=0&amp;utmp=%2Fshop%2Findex.php%3Froute%3Daccount%2Flogin&amp;utmac=UA-18544629-2&amp;utmcc=__utma%3D177737767.422066386.1289975096.1289975096.1289975096.1%3B%2B__utmz%3D177737767.1289975096.1.1.utmcsr%3D(direct)%7Cutmccn%3D(direct)%7Cutmcmd%3D(none)%3B&amp;utmu=q" content_bytes="35"/>
            <TXN_DETAIL_STATUS status_code="200"/>
          </TXN_PAGE_ELEMENT>
        </TXN_PAGE_DETAILS>
      </TXN_PAGE>
    </TXN_MEASUREMENT>
  </DP_TXN_MEASUREMENTS>
</TXN_DATA_FEED>
'''
