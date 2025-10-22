import json
import os
import shutil
import copy
import time
import xml.etree.cElementTree as ET
import lxml.etree as etree
from pkg_resources import resource_filename
import yaml
import cyrtranslit
import random
import string
import re
from datetime import datetime
from .util import apply_template_dir, copy_dir, filter_name
import tempfile
import zipfile
import hashlib
import mimetypes

_BUILD_PATH = "_build"
_EXPORT_PATH = "export"
_BUILD_YAML_PATH = "_build/index.yaml"
_BUILD_STATIC_PATH = "_build/_static"
_BUILD_IMAGE_PATH = "_build/_image"


class ScormPackager:

    _LOCALAZIE_STRIGNS = {
        'en': {"About": "About the course"},
        'sr': {"About": "O kursu"},
        'sr-Latn': {"About": "O kursu"},
        'sr-Cyrl': {"About": "О курсу"},
    }

    def __init__(self):
        manifest = ET.Element("manifest",
                              identifier="manifest_" + datetime.now().strftime("%d-%b-%Y-%H-%M-"),
                              version="1.0",
                              xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2")

        manifest.set("xmlns:adlcp", "http://www.adlnet.org/xsd/adlcp_rootv1p2")
        manifest.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        manifest.set("xsi:schemaLocation", "http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd http://www.imsglobal.org/xsd/imsmd_rootv1p2p1 imsmd_rootv1p2p1.xsd http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd")

        metadata = ET.SubElement(manifest, "metadata")

        ET.SubElement(metadata, "schema").text = "ADL SCORM"
        ET.SubElement(metadata, "schemaversion").text = "1.2"

        organizations = ET.SubElement(
            manifest, "organizations", default="petlja_org")
        resources = ET.SubElement(manifest, "resources")

        common_resource = ET.SubElement(
            resources, "resource", identifier="common_files", type="webcontent")
        common_resource.set("adlcp:scormtype", "asset")

        for root, _, files in os.walk(_BUILD_STATIC_PATH):
            for file in files:
                relative_path = os.path.join(root, file).replace(
                    "_build", ".").replace("\\", "/")
                file = ET.SubElement(
                    common_resource, "file", href=relative_path)

        for root, _, files in os.walk(_BUILD_IMAGE_PATH):
            for file in files:
                relative_path = os.path.join(root, file).replace(
                    "_build", ".").replace("\\", "/")
                file = ET.SubElement(
                    common_resource, "file", href=relative_path)

        self.manifest_template = [manifest, organizations, resources]
        self._skip_files = ["doctrees", "_sources", ".buildinfo", "search.html",
                            "searchindex.js", "objects.inv", "pavement.py", "course-errors.js", "genindex.html", "index.yaml"]

        self._load_data_from_yaml()
        if self.course_data:
            for lesson in self.course_data["lessons"]:
                self._skip_files.append(lesson["folder"])

            self.course_lang = self.course_data['lang'] if self.course_data[
                'lang'] in ScormPackager._LOCALAZIE_STRIGNS else 'en'

    def _load_data_from_yaml(self):
        try:
            with open(_BUILD_YAML_PATH, encoding="utf8") as f:
                self.course_data = yaml.load(f, Loader=yaml.FullLoader)
        except IOError:
            self.course_data = None

    def create_package_for_course(self):
        self._create_imsmanifest_for_course()
        self._create_archive_for_course()

    def create_package_for_single_sco_course(self):
        self._create_imsmanifest_for_single_sco_course()
        self._create_archive_for_course()

    def create_packages_for_lectures(self):
        if not self.course_data:
            return None
        if not os.path.exists(_EXPORT_PATH):
            os.mkdir(_EXPORT_PATH)
        for lesson in self.course_data["lessons"]:
            if not os.path.exists(os.path.join(_EXPORT_PATH, cyrtranslit.to_latin(lesson["normalized_title"]))):
                os.mkdir(os.path.join(_EXPORT_PATH,
                                      cyrtranslit.to_latin(lesson["normalized_title"])))
            self._skip_files.remove(lesson["folder"])
            copy_dir(_BUILD_PATH, os.path.join(
                _EXPORT_PATH, cyrtranslit.to_latin(lesson["normalized_title"])), self._filter_by_name)
            self._skip_files.append(lesson["folder"])

            manifest, organizations, resources = copy.deepcopy(
                self.manifest_template)
            organization = ET.SubElement(
                organizations, "organization", identifier="petlja_org")
            ET.SubElement(organization, "title").text = lesson["title"]
            lecture_item = ET.SubElement(
                organization, "item", identifier=self._get_random_string_for_id())
            ET.SubElement(lecture_item, "title").text = lesson["title"]
            for activity in lesson["activities"]:
                resource_id = self._create_id(
                    lesson["title"], activity["title"])
                activity_item = ET.SubElement(
                    lecture_item, "item", identifier=self._get_random_string_for_id(), identifierref=resource_id)
                ET.SubElement(activity_item, "title").text = activity["title"]
                resource = ET.SubElement(resources, "resource", identifier=resource_id, type="webcontent", href=os.path.join(
                    lesson["folder"], activity["file"]).replace("\\", "/"))
                resource.set("adlcp:scormtype", "sco")
                ET.SubElement(resource, "file", href=os.path.join(
                    lesson["folder"], activity["file"]).replace("\\", "/"))
                ET.SubElement(resource, "dependency",
                              identifierref="common_files")

            tree = ET.ElementTree(manifest)

            manifest_path = os.path.join(os.path.join(
                _EXPORT_PATH, cyrtranslit.to_latin(lesson["normalized_title"])), "imsmanifest.xml")
            tree.write(manifest_path)

            x = etree.parse(manifest_path)
            with open(manifest_path, mode="w+", encoding="utf-8") as file:
                file.write(etree.tostring(x, pretty_print=True, encoding=str))

            self._create_archive_for_lecutres(
                cyrtranslit.to_latin(lesson["normalized_title"]))

    def create_single_sco_packages_for_lectures(self):
        if not self.course_data:
            return None
        if not os.path.exists(_EXPORT_PATH):
            os.mkdir(_EXPORT_PATH)
        for lesson in self.course_data["lessons"]:
            if not os.path.exists(os.path.join(_EXPORT_PATH, cyrtranslit.to_latin(lesson["normalized_title"]))):
                os.mkdir(os.path.join(_EXPORT_PATH,
                                      cyrtranslit.to_latin(lesson["normalized_title"])))
            self._skip_files.remove(lesson["folder"])
            copy_dir(_BUILD_PATH, os.path.join(
                _EXPORT_PATH, cyrtranslit.to_latin(lesson["normalized_title"])), self._filter_by_name)
            self._skip_files.append(lesson["folder"])

            manifest, organizations, resources = copy.deepcopy(
                self.manifest_template)
            organization = ET.SubElement(
                organizations, "organization", identifier="petlja_org")
            ET.SubElement(organization, "title").text = lesson["title"]
            lecture_item = ET.SubElement(
                organization, "item", identifier=self._get_random_string_for_id())
            ET.SubElement(lecture_item, "title").text = lesson["title"]

            activity = lesson["activities"][0]
            resource_id = self._create_id(lesson["title"], activity["title"])
            activity_item = ET.SubElement(
                lecture_item, "item", identifier=self._get_random_string_for_id(), identifierref=resource_id)
            ET.SubElement(activity_item, "title").text = activity["title"]
            resource = ET.SubElement(resources, "resource", identifier=resource_id, type="webcontent", href=os.path.join(
                lesson["folder"], activity["file"]).replace("\\", "/"))
            resource.set("adlcp:scormtype", "sco")
            ET.SubElement(resource, "file", href=os.path.join(
                lesson["folder"], activity["file"]).replace("\\", "/"))
            for activity in lesson["activities"][1:]:
                ET.SubElement(resource, "file", href=os.path.join(
                    lesson["folder"], activity["file"]).replace("\\", "/"))

            ET.SubElement(resource, "dependency", identifierref="common_files")
            tree = ET.ElementTree(manifest)
            manifest_path = os.path.join(os.path.join(
                _EXPORT_PATH, cyrtranslit.to_latin(lesson["normalized_title"])), "imsmanifest.xml")
            tree.write(manifest_path)

            x = etree.parse(manifest_path)
            with open(manifest_path, mode="w+", encoding="utf-8") as file:
                file.write(etree.tostring(x, pretty_print=True, encoding=str))

            self._create_archive_for_lecutres(
                cyrtranslit.to_latin(lesson["normalized_title"]))

    def _create_imsmanifest_for_course(self):
        if not self.course_data:
            return None
        manifest, organizations, resources = copy.deepcopy(
            self.manifest_template)
        organization = ET.SubElement(
            organizations, "organization", identifier="petlja_org")
        ET.SubElement(organization, "title").text = self.course_data["title"]
        # Setup a homepage as index.html
        lecture_item = ET.SubElement(
            organization, "item", identifier="home_page")
        ET.SubElement(lecture_item, "title").text = self.course_data["title"]
        activity_item = ET.SubElement(
            lecture_item, "item", identifier="indexid", identifierref="index")
        ET.SubElement(
            activity_item, "title").text = ScormPackager._LOCALAZIE_STRIGNS[self.course_lang]['About']
        resource = ET.SubElement(
            resources, "resource", identifier="index", type="webcontent", href="index.html")
        resource.set("adlcp:scormtype", "sco")
        ET.SubElement(resource, "file", href="index.html")

        for lesson in self.course_data["lessons"]:
            lecture_item = ET.SubElement(
                organization, "item", identifier=self._get_random_string_for_id())
            ET.SubElement(lecture_item, "title").text = lesson["title"]
            for activity in lesson["activities"]:
                resource_id = self._create_id(
                    lesson["title"], activity["title"])
                activity_item = ET.SubElement(
                    lecture_item, "item", identifier=self._get_random_string_for_id(), identifierref=resource_id)
                ET.SubElement(activity_item, "title").text = activity["title"]
                resource = ET.SubElement(resources, "resource", identifier=resource_id, type="webcontent", href=os.path.join(
                    lesson["folder"], activity["file"]).replace("\\", "/"))
                resource.set("adlcp:scormtype", "sco")
                ET.SubElement(resource, "file", href=os.path.join(
                    lesson["folder"], activity["file"]).replace("\\", "/"))
                ET.SubElement(resource, "dependency",
                              identifierref="common_files")

        manifest_path = os.path.join(_BUILD_PATH, "imsmanifest.xml")
        tree = ET.ElementTree(manifest)
        tree.write(manifest_path)

        x = etree.parse(manifest_path)
        with open(manifest_path, mode="w+", encoding="utf-8") as file:
            file.write(etree.tostring(x, pretty_print=True, encoding=str))

    def _create_imsmanifest_for_single_sco_course(self):
        if not self.course_data:
            return None
        manifest, organizations, resources = copy.deepcopy(
            self.manifest_template)
        organization = ET.SubElement(
            organizations, "organization", identifier="petlja_org")
        ET.SubElement(organization, "title").text = self.course_data["title"]
        # Setup a homepage as index.html
        lecture_item = ET.SubElement(
            organization, "item", identifier="home_page")
        ET.SubElement(lecture_item, "title").text = self.course_data["title"]
        activity_item = ET.SubElement(
            lecture_item, "item", identifier="indexid", identifierref="index")
        ET.SubElement(
            activity_item, "title").text = ScormPackager._LOCALAZIE_STRIGNS[self.course_lang]['About']
        resource = ET.SubElement(
            resources, "resource", identifier="index", type="webcontent", href="index.html")
        resource.set("adlcp:scormtype", "sco")
        ET.SubElement(resource, "file", href="index.html")

        for lesson in self.course_data["lessons"]:
            for activity in lesson["activities"]:
                ET.SubElement(resource, "file", href=os.path.join(
                    lesson["folder"], activity["file"]).replace("\\", "/"))

        ET.SubElement(resource, "dependency", identifierref="common_files")

        manifest_path = os.path.join(_BUILD_PATH, "imsmanifest.xml")
        tree = ET.ElementTree(manifest)
        tree.write(manifest_path)

        x = etree.parse(manifest_path)
        with open(manifest_path, mode="w+", encoding="utf-8") as file:
            file.write(etree.tostring(x, pretty_print=True, encoding=str))

    def _create_archive_for_course(self):
        if not self.course_data:
            return None
        _path = os.path.join(
            _EXPORT_PATH, cyrtranslit.to_latin(self.course_data["title"]))
        copy_dir(_BUILD_PATH, _path, filter_name)
        shutil.make_archive(_path, "zip", _path)
        shutil.rmtree(_path)

    def _create_archive_for_lecutres(self, title):
        if not self.course_data:
            return None
        shutil.make_archive(os.path.join(_EXPORT_PATH, title),
                            "zip", os.path.join(_EXPORT_PATH, title))
        shutil.rmtree(os.path.join(_EXPORT_PATH, title))

    def _filter_by_name(self, item):
        if item not in self._skip_files:
            return True
        else:
            return False

    def _get_random_string_for_id(self):
        return ''.join((random.choice(string.ascii_lowercase) for x in range(10)))

    def _create_id(self, lesson_title, activity_title):
        return re.sub(r'\W+', '', 'r_' + cyrtranslit.to_latin(lesson_title + "_" + activity_title).replace(" ", "_"))


class ScormProxyPackager:
    def __init__(self) -> None:
        with open(_BUILD_YAML_PATH, encoding="utf8") as f:
            self.course_yaml_data = yaml.load(f, Loader=yaml.FullLoader)
        self.courseId = os.path.basename(os.getcwd())  
        try:
            with open('package-conf.json') as json_file:
                self.package_conf = json.load(json_file)
        except FileNotFoundError:
            print("Missing package-conf.json.")
            exit()
        
        with open('course.json') as json_file:
            self.course_data = json.load(json_file)
        self.package_conf['title'] = cyrtranslit.to_latin(normalize(self.course_data['title']))
        self.package_conf["identifier"] = (self.course_data['courseId'])

    def create_package_for_course(self):
        zip_path = os.path.join(_EXPORT_PATH,  self.courseId + '_scorm')
        apply_template_dir(resource_filename('petljadoc', 'scorm-proxy-templates'), zip_path, self.package_conf)
        with open(os.path.join(zip_path, 'course.json'), mode="w+") as f:
            f.write(json.dumps(self.course_data))
        shutil.make_archive(zip_path, "zip", zip_path)
        shutil.rmtree(zip_path)

    def create_packages_for_activities(self):
        single_activity_dict = {}
        for lesson in self.course_data["active_lessons"]:
            dict_image = copy.deepcopy(self.course_data)
            for activity in lesson["active_activities"]:
                single_activity_dict["active_lessons"] = []
                single_activity_dict["active_lessons"].append(lesson)
                single_activity_dict["active_lessons"][0]["active_activities"] = []
                single_activity_dict["active_lessons"][0]["active_activities"].append(activity)
                dict_image["active_lessons"] = single_activity_dict["active_lessons"]
                zip_path = os.path.join(_EXPORT_PATH,   self.courseId+ '_scorm_aktivnosti' , cyrtranslit.to_latin(lesson["normalized_title"]) , cyrtranslit.to_latin(normalize(activity['title'])))
                apply_template_dir(resource_filename('petljadoc', 'scorm-proxy-templates'), zip_path, self.package_conf)
                with open(os.path.join(zip_path, 'course.json'), mode="w+") as f:
                    f.write(json.dumps(dict_image))
                shutil.make_archive(zip_path, "zip", zip_path)
                shutil.rmtree(zip_path)
        zip_path = os.path.join(_EXPORT_PATH,   self.courseId+ '_scorm_aktivnosti')
        shutil.make_archive(zip_path, "zip", zip_path)
        shutil.rmtree(zip_path)
    



    def create_moodle_backup(self):
        archive_index_lines = []

        course_id = os.path.basename(os.getcwd())
        course_scorm_zip_path = course_id + '_scorm_aktivnosti.zip'
        course_scorm_zip_path = os.path.join(_EXPORT_PATH, course_scorm_zip_path)

        temp_dir = tempfile.TemporaryDirectory()
        moodle_backup_file = zipfile.ZipFile(_EXPORT_PATH + '/'+ course_id + '.mbz', 'w')
        activity_count=0
        for lesson in self.course_yaml_data["lessons"]:
            for activity in lesson["activities"]:
                activity_count += 1
        activity_aggregationcoef2 = round(1/activity_count,5)
        sort_order = 0
        section_sort_order = 0
        with zipfile.ZipFile(course_scorm_zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir.name)
            moodle_course = MoodleCourse(self.course_yaml_data)
            moodle_backup_file.write(temp_dir.name, 'course')
            copied_files = []
            for lesson in self.course_yaml_data["lessons"]:
                section_sort_order += 1
                moodle_section = MoodleSection(lesson, section_sort_order)
                moodle_course.sections.append(moodle_section)
                moodle_backup_file.write(temp_dir.name, moodle_section.section_dir_path)
                for activity in lesson["activities"]:
                    sort_order += 1
                    moodle_activity = MoodleActivity(activity,activity_aggregationcoef2, sort_order, course_id)
                    moodle_section.add_activity(moodle_activity)
                    moodle_backup_file.write(temp_dir.name, moodle_activity.activity_dir_path)
                    scorm_activity_zip_path = os.path.join(getNormalizedLatinEntry(lesson,"normalized_title") , getNormalizedLatinEntry(activity,"normalized_title"))
                    file_path = os.path.join(temp_dir.name, scorm_activity_zip_path + '.zip')
                    moodle_activity.sah1 = Sha1Hasher(file_path)
                    moodle_activity.file_size = str(os.path.getsize(file_path))
                    with zipfile.ZipFile(file_path, 'r') as zip_scorm_file_ref:
                        temp_dir_scorm = tempfile.TemporaryDirectory()
                        zip_scorm_file_ref.extractall(temp_dir_scorm.name)
                        moodle_activity.add_file(MoodleFile('.', 'da39a3ee5e6b4b0d3255bfef95601890afd80709', '$@NULL@$', '', '0','content'))
                        moodle_activity.add_file(MoodleFile('.', 'da39a3ee5e6b4b0d3255bfef95601890afd80709', '$@NULL@$', '', '0', 'package'))
                        for file in os.listdir(temp_dir_scorm.name):
                            path = os.path.join(temp_dir_scorm.name, file)
                            hash_file_name = Sha1Hasher(path)
                            mime_type, _ = mimetypes.guess_type(path)
                            rel_path = os.path.relpath(path, temp_dir_scorm.name)
                            file_size = os.path.getsize(path)     
                            moodle_file = MoodleFile(file, hash_file_name, mime_type, rel_path, file_size, 'content')
                            moodle_activity.add_file(moodle_file)
                            if hash_file_name not in copied_files:
                                copied_files.append(hash_file_name)
                                moodle_backup_file.write(path, 'files/' +hash_file_name[0:2] +'/' + hash_file_name)               
                    moodle_activity.add_file(MoodleFile(file_path,moodle_activity.sah1,'$@NULL@$', '', '0','content'))
                    moodle_backup_file.write(file_path, 'files/' +moodle_activity.sah1[0:2] +'/' + moodle_activity.sah1)
                    moodle_activity.extract_activity_data()
                    apply_moodle_template_dir(resource_filename('petljadoc', 'moodle-templates/activities'),moodle_backup_file, root_copy_path = moodle_activity.activity_dir_path, xml_data = moodle_activity.xml_data)
                    
                moodle_section.extract_section_data()
                apply_moodle_template_dir(resource_filename('petljadoc', 'moodle-templates/sections'), moodle_backup_file, root_copy_path = moodle_section.section_dir_path, xml_data = moodle_section.xml_data)
            moodle_course.extract_corse_data()
            apply_moodle_template_dir(resource_filename('petljadoc', 'moodle-templates'),moodle_backup_file, filter_name=['activities','sections'], xml_data = moodle_course.xml_data)
        moodle_backup_file.close()
        temp_dir.cleanup()

        temp_dir = tempfile.TemporaryDirectory()
        with zipfile.ZipFile(_EXPORT_PATH + '/'+ course_id + '.mbz', 'a') as zip_ref:
            zip_ref.extractall(temp_dir.name)
            total_entries = 0
            for root, dirs, files in os.walk(temp_dir.name):
                total_entries += len(files) + len(dirs)
            for root, dirs, files in os.walk(temp_dir.name):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, temp_dir.name).replace('\\', '/') 
                    file_size = os.path.getsize(file_path)
                    creation_time = round(os.path.getctime(file_path))
                    archive_index_lines.append(rel_path + '\tf\t' + str(file_size) +'\t'+ str(creation_time))
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    rel_path = os.path.relpath(dir_path, temp_dir.name).replace('\\', '/') 
                    archive_index_lines.append(rel_path + '/'+ '\td\t' + '0\t?')
            archive_index_lines.sort()
            archive_index_lines.insert(0,('Moodle archive file index. Count: ' + str(total_entries) ))

            zip_ref.writestr('.ARCHIVE_INDEX', '\n'.join(archive_index_lines))
            
            zip_ref.close()
       

class MoodleSection:
    def __init__(self,lesson_yaml_block, sort_order):
        self.id = get_unused_id()
        self.sort_order = sort_order
        self.title = lesson_yaml_block["title"]
        self.activities = []
        self.section_dir_path = '/sections/section_' + str(self.id)
        self.xml_data = {}

    def extract_section_data(self):
        time_stamp = get_time_stamp()
        self.xml_data = {
            'section' : {
                "attributes" : {"id" :self.id},
                './number' : str(self.sort_order),
                './name' :  self.title,
                './sequence' :  ','.join([activity.module_id for activity in self.activities]),
                './timemodified' : time_stamp,
            }
        }

    def add_activity(self, activity):
        self.activities.append(activity)
        activity.section_id = self.id
        activity.section_order = self.sort_order

class MoodleCourse:
    def __init__(self, course_yaml_data):
        self.course_yaml_data = course_yaml_data
        self.sections = []
        self.activity_et_elements = []
        self.section_et_elements = []
        self.setting_et_elements = []
        self.file_et_elements = []
        self.xml_data = {}

    def extract_corse_data(self):
        self._make_file_et_elements()
        time_stamp = get_time_stamp()
        self.xml_data = {
            'moodle_backup' : {
                "./information/name" : "-".join([self.course_yaml_data["courseId"],'nu.mbz']),
                "./information/backup_date" : time_stamp,
                "./information/original_course_fullname"  :self.course_yaml_data["title"],
                "./information/original_course_shortname" : self.course_yaml_data["courseId"],
                "./information/original_course_startdate"  : time_stamp,
                "./information/contents/course/title" : self.course_yaml_data["courseId"],
                "./information/settings/setting[1]/value" :  "-".join([self.course_yaml_data["courseId"],'nu.mbz']),
                "./information/contents/activities" : self.activity_et_elements,
                "./information/contents/sections" : self.section_et_elements,
                "./information/settings" : self.setting_et_elements,
            },
            'files' : {
                "root_elements" : self.file_et_elements
            },
            'course':{
                "./shortname" : self.course_yaml_data["courseId"],
                "./fullname" : self.course_yaml_data["title"],
                "./summary" : self.course_yaml_data["description"]["shortDescription"],
                "./startdate" : time_stamp,
                "./timecreated" : time_stamp,
                "./timemodified" : time_stamp,
            },
        }

    def _make_file_et_elements(self):
        for section in self.sections:
            self.section_et_elements.append(self._make_et_section_element(section))
            for activity in section.activities:
                self.activity_et_elements.append(self._make_activity_et_element(section, activity))
                for file in activity.activity_files:
                    el = self._make_file_et_element(file,activity)
                    self.file_et_elements.append(el)

        for section in self.sections:
            self.setting_et_elements.append(self._make_setting_et_element_section_included(section))
            self.setting_et_elements.append(self._make_setting_et_element_section_userinfo(section))
            for activity in section.activities: 
                self.setting_et_elements.append(self._make_setting_et_element_activity_included(activity))         
                self.setting_et_elements.append(self._make_setting_et_element_activity_userinfo(activity))  
                self.file_et_elements.append(self._make_activity_file_et_elements(activity))

    
    def _make_activity_file_et_elements(self, activity):
        el = ET.Element("file",{"id":get_unused_id()})
        ET.SubElement(el, "contenthash").text = activity.sah1 
        ET.SubElement(el, "contextid").text = activity.context_id
        ET.SubElement(el, "component").text ='mod_scorm'
        ET.SubElement(el, "filearea").text = 'content'
        ET.SubElement(el, "itemid").text = '0'
        ET.SubElement(el, "filepath").text = '/'
        ET.SubElement(el, "filename").text = (getNormalizedLatinEntry(activity.activity_yaml_block, "normalized_title") + ".zip")
        ET.SubElement(el, "userid").text = '$@NULL@$'
        ET.SubElement(el, "filesize").text = activity.file_size
        ET.SubElement(el, "mimetype").text ="application/zip"
        ET.SubElement(el, "status").text = '0'
        ET.SubElement(el, "timecreated").text = get_time_stamp()
        ET.SubElement(el, "timemodified").text = get_time_stamp()
        ET.SubElement(el, "source").text = (getNormalizedLatinEntry(activity.activity_yaml_block, "normalized_title") + ".zip")
        ET.SubElement(el, "author").text = 'Petlja'
        ET.SubElement(el, "license").text = 'allrightsreserved'
        ET.SubElement(el, "sortorder").text = '0'
        ET.SubElement(el, "repositorytype").text = '$@NULL@$'
        ET.SubElement(el, "repositoryid").text = '$@NULL@$'
        ET.SubElement(el, "reference").text = '$@NULL@$'

        return el

    def _make_dummy_et_elements(self, activity):
        el = ET.Element("file",{"id":get_unused_id()})
        ET.SubElement(el, "contenthash").text = activity.sah1 
        ET.SubElement(el, "contextid").text = activity.context_id
        ET.SubElement(el, "component").text ='mod_scorm'
        ET.SubElement(el, "filearea").text = 'content'
        ET.SubElement(el, "itemid").text = '0'
        ET.SubElement(el, "filepath").text = '/'
        ET.SubElement(el, "filename").text = '.'
        ET.SubElement(el, "userid").text = '1'
        ET.SubElement(el, "filesize").text = '0'
        ET.SubElement(el, "mimetype").text ="$@NULL@$"
        ET.SubElement(el, "status").text = '0'
        ET.SubElement(el, "timecreated").text = get_time_stamp()
        ET.SubElement(el, "timemodified").text = get_time_stamp()
        ET.SubElement(el, "source").text = '$@NULL@$'
        ET.SubElement(el, "author").text = '$@NULL@$'
        ET.SubElement(el, "license").text = '$@NULL@$'
        ET.SubElement(el, "sortorder").text = '0'
        ET.SubElement(el, "repositorytype").text = '$@NULL@$'
        ET.SubElement(el, "repositoryid").text = '$@NULL@$'
        ET.SubElement(el, "reference").text = '$@NULL@$'

        return el

    def _make_file_et_element(self,file,activity):
        el = ET.Element("file",{"id":file.id})
        ET.SubElement(el, "contenthash").text = file.hash_file_name
        ET.SubElement(el, "contextid").text = activity.context_id
        ET.SubElement(el, "component").text ='mod_scorm'
        ET.SubElement(el, "filearea").text = file.filearea
        ET.SubElement(el, "itemid").text = '0'
        ET.SubElement(el, "filepath").text = '/'
        ET.SubElement(el, "filename").text = os.path.basename(file.path)
        ET.SubElement(el, "userid").text = '$@NULL@$'
        ET.SubElement(el, "filesize").text = str(file.size)
        ET.SubElement(el, "mimetype").text = file.mime_type
        ET.SubElement(el, "status").text = '0'
        ET.SubElement(el, "timecreated").text = get_time_stamp()
        ET.SubElement(el, "timemodified").text = get_time_stamp()
        ET.SubElement(el, "source").text = '$@NULL@$'
        ET.SubElement(el, "author").text = '$@NULL@$'
        ET.SubElement(el, "license").text = '$@NULL@$'
        ET.SubElement(el, "sortorder").text = '0'
        ET.SubElement(el, "repositorytype").text = '$@NULL@$'
        ET.SubElement(el, "repositoryid").text = '$@NULL@$'
        ET.SubElement(el, "reference").text = '$@NULL@$'

        return el

    def _make_et_section_element(self, section):
        el = ET.Element("section")
        ET.SubElement(el, "sectionid").text = section.id
        ET.SubElement(el, "title").text = section.title
        ET.SubElement(el, "directory").text = section.section_dir_path.lstrip('/') 

        return el
    
    def _make_activity_et_element(self,section, activity):
        el = ET.Element("activity")
        ET.SubElement(el, "moduleid").text = activity.module_id
        ET.SubElement(el, "sectionid").text = section.id
        ET.SubElement(el, "modulename").text = 'scorm'
        ET.SubElement(el, "title").text = activity.activity_yaml_block["title"]
        ET.SubElement(el, "directory").text = activity.activity_dir_path.lstrip('/') 
        
        return el

    def _make_setting_et_element_section_included(self,section):
        el = ET.Element("setting")
        ET.SubElement(el, "level").text = 'section'
        ET.SubElement(el, "section").text = 'section_' + section.id
        ET.SubElement(el, "name").text = 'section_' + section.id + '_included'
        ET.SubElement(el, "value").text ='1'
        
        return el

    
    def _make_setting_et_element_section_userinfo(self,section):
        el = ET.Element("setting")
        ET.SubElement(el, "level").text = 'section'
        ET.SubElement(el, "section").text = 'section_' + section.id
        ET.SubElement(el, "name").text = 'section_' + section.id + '_userinfo'
        ET.SubElement(el, "value").text ='0'
        
        return el

    def _make_setting_et_element_activity_included(self,activity):
        el = ET.Element("setting")
        ET.SubElement(el, "level").text = 'activity'
        ET.SubElement(el, "activity").text = 'scorm_' + activity.module_id
        ET.SubElement(el, "name").text = 'scorm_' + activity.module_id + '_included'
        ET.SubElement(el, "value").text ='1'
        
        return el
    
    def _make_setting_et_element_activity_userinfo(self,activity):
        el = ET.Element("setting")
        ET.SubElement(el, "level").text = 'activity'
        ET.SubElement(el, "activity").text = 'scorm_' + activity.module_id
        ET.SubElement(el, "name").text = 'scorm_' + activity.module_id + '_userinfo'
        ET.SubElement(el, "value").text = '0'
        
        return el

class MoodleActivity:
    def __init__(self, activity_yaml_block, aggregationcoef2, sort_order,course_id):
        self.course_id = course_id
        self.context_id = get_unused_id()
        self.module_id = get_unused_id()
        self.id = get_unused_id()
        self.sort_order = sort_order
        self.activity_yaml_block = activity_yaml_block
        self.activity_dir_path = 'activities/scorm_' + str(self.module_id)
        self.time_stamp = get_time_stamp()
        self.aggregationcoef2 = aggregationcoef2
        self.grade_item_id = str(get_unused_id())
        self.file_ref_et_elem = []
        self.activity_files = []
        self.xml_data = {}

    def add_file(self,file):
        self.activity_files.append(file)

    def _make_file_inforef_element(self, id):
        el = ET.Element('file')
        ET.SubElement(el, 'id').text= id
        return el

    def extract_activity_data(self):
        self.xml_data = {
            'activity_gradebook' : {
                "./grade_items/grade_item" : {"id" :  self.grade_item_id},
                "./grade_items/grade_item/categoryid" : get_unused_id(),
                "./grade_items/grade_item/itemname" : self.activity_yaml_block["title"],
                "./grade_items/grade_item/iteminstance" : str(self.sort_order - 1),
                "./grade_items/grade_item/aggregationcoef2" : str(self.aggregationcoef2),
                "./grade_items/grade_item/sortorder" : str(self.sort_order),
                "./grade_items/grade_item/timecreated" : self.time_stamp,
                "./grade_items/grade_item/timemodified" : self.time_stamp,
            },
            'module' : {
                "attributes" : {"id" : self.module_id},
                "./sectionid" :  str(self.section_id),
                "./sectionnumber" : str(self.section_order),
                "./added" : self.time_stamp,
            },
            "inforef" : {
                "./fileref" : [self._make_file_inforef_element(file.id) for file in self.activity_files],
                ".grade_itemref/grade_item/id": self.grade_item_id,
            },
            "activity" :{
                "attributes" : {"id": self.id, "moduleid" : self.module_id, "contextid" : self.context_id},
                "./scorm" : {"id" : self.id},
                "./scorm/name" : self.activity_yaml_block["title"],
                "./scorm/reference" :   getNormalizedLatinEntry(self.activity_yaml_block, "normalized_title")+".zip",
                "./scorm/sha1hash" : self.sah1,
                "./scorm/revision" : '1',
                "./scorm/launch" : '1',
                "./scorm/timemodified" : self.time_stamp,
                "./scorm/scoes/sco[1]" : {"id" :get_unused_id()},
                "./scorm/scoes/sco[1]/manifest" : self.course_id,
                "./scorm/scoes/sco[2]" : {"id" : get_unused_id()},
                "./scorm/scoes/sco[2]/manifest" : self.course_id,
                "./scorm/scoes/sco[2]/sco_datas/sco_data[1]" : {"id" :get_unused_id()},
                "./scorm/scoes/sco[2]/sco_datas/sco_data[2]" : {"id" : get_unused_id()},
                "./scorm/scoes/sco[3]" : {"id" : get_unused_id()},
                "./scorm/scoes/sco[3]/manifest" : self.course_id,
                "./scorm/scoes/sco[3]/sco_datas/sco_data[1]" : {"id" : get_unused_id()},
                "./scorm/scoes/sco[3]/sco_datas/sco_data[2]" : {"id" : get_unused_id()},
                
            }
        }

class MoodleFile:
    def __init__(self,path, hash_file_name, mime_type, rel_path, file_size, filearea):
        self.path = path
        self.id = get_unused_id() 
        self.hash_file_name = hash_file_name
        self.mime_type = mime_type    
        self.rel_path = rel_path
        self.size = file_size
        self.filearea = filearea


class IdGenerator:
    _instance = None
    id = 200

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = IdGenerator()
        return cls._instance

    def get_unused_id(self):
        # Increment the id
        self.id += 1
        # Return the unused id
        return str(self.id)
    
    
def get_unused_id():
    return IdGenerator.get_instance().get_unused_id()

def get_time_stamp():
    return str(round(time.time()))

def Sha1Hasher(file_path):

    buf_size = 65536
    sha1 = hashlib.sha1()

    with open(file_path, 'rb') as f:
        while True:
            data = f.read(buf_size)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()

def getNormalizedLatinEntry(yaml_block, yaml_key):
    return cyrtranslit.to_latin(yaml_block[yaml_key])

def copy_xml_file(xml_template_file_path, data, zip_ref, zip_file_path):
    tree = ET.parse(xml_template_file_path)
    root = tree.getroot()
    if data.get(root.tag):
        if data[root.tag].get("attributes"):
            attribute_dict = data[root.tag].pop("attributes")
            for attribute_key, attribute_value in attribute_dict.items():
                root.set(attribute_key, attribute_value)
        if data[root.tag].get("root_elements"):
            et_element = data[root.tag].pop("root_elements")
            if isinstance(et_element, list):
                for el in et_element:
                    root.append(el)
        for key, value in data[root.tag].items():
            element = root.find(key)
            if element is not None:
                if isinstance(value, list):
                    for el in value:
                        element.append(el)
                elif isinstance(value, dict):
                    for k, v in value.items():
                        element.set(k, v)
                else:
                    element.text = value

    temp_file = tempfile.NamedTemporaryFile(mode='w+b', delete=False)
    temp_file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n".encode())
    ET.ElementTree(root).write(temp_file)
    temp_file.flush() 
    zip_ref.write(temp_file.name, zip_file_path)
    temp_file.close()
    os.unlink(temp_file.name)

def apply_moodle_template_dir(src_dir, zip_ref, filter_name=None, root_copy_path = '', xml_data = {}):
    for item in os.listdir(src_dir):
        if filter_name and item in filter_name:
            continue
        s = os.path.join(src_dir, item)
        if os.path.isdir(s):
            apply_moodle_template_dir(s, zip_ref,  filter_name, root_copy_path, xml_data)
        else:
            d = os.path.relpath(s, resource_filename('petljadoc', 'moodle-templates'))
            if root_copy_path:
                d = os.path.join(root_copy_path , os.path.basename(d))
            if d.endswith('.xml'):
                copy_xml_file(s, xml_data, zip_ref, d)
            else:
                zip_ref.write(s, d)




def normalize(string: str):
    reserved_chars = ['?', '>', ':', '"', '/', '\\', '|', '*']
    return ''.join(char for char in string if char not in reserved_chars).rstrip('.')
