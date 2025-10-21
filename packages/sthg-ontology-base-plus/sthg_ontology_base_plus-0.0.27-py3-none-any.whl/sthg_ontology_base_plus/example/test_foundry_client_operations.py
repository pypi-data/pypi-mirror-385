# from enums.http_enum import HttpStatus
from ontology_new.ontology_sdk import FoundryClient
from ontology_new.ontology_sdk.Object import ppl_people, ppl_people_picture
# from utils.response import ResCode
# from utils.utils import parse_pagination_params
from dataclasses import dataclass
from typing import Optional



def parse_pagination_params(query_params: dict, default_page: int = 1, default_page_size: int = 10) -> tuple[int, int]:
    """
    从请求参数解析分页配置（page 和 page_size），返回 (offset, limit)。
    如果参数无效，使用默认值。
    """
    try:
        page = max(1, int(query_params.get("page", default_page)))
        page_size = max(1, int(query_params.get("page_size", default_page_size)))
        offset = (page - 1) * page_size
        return offset, page_size
    except (ValueError, TypeError):
        return 0, default_page_size  # 参数无效时返回默认 offset=0, limit=default_page_size

@dataclass
class IndexRequest:
    person_type: Optional[str] = None  # 人物类型 1.政宠 2.军人 3.商人 4.其他
    country_code: Optional[str] = None  # 国家编码
    gender: Optional[int] = None  # 性别 1.男 2.女
    date_of_birth: Optional[str] = None  # 出生日期
    marital_status: Optional[str] = None  # 婚姻状况 1.未婚 2.已婚 3.离异 4.丧偶
    religion: Optional[str] = None  # 宗教 党派
    identity_type: Optional[int] = None  # 证件类型:1:身份证2:社保3:护照
    identity_no: Optional[str] = None  # 证件号码
    page: Optional[int] = 1
    page_size: Optional[int] = 10

#
# class RwUserService:
#
#     def get_user_list(self, req: IndexRequest):
#         try:
#             client = FoundryClient()
#             conditions = []
#             if req.person_type:
#                 conditions.append(ppl_people.person_type == req.person_type)
#             if req.country_code:
#                 conditions.append(ppl_people.country_code == req.country_code)
#             if req.gender:
#                 conditions.append(ppl_people.gender == req.gender)
#             if req.date_of_birth:
#                 conditions.append(ppl_people.date_of_birth == req.date_of_birth)
#             if req.marital_status:
#                 conditions.append(ppl_people.marital_status == req.marital_status)
#             if req.religion:
#                 conditions.append(ppl_people.religion == req.religion)
#             if req.identity_type and req.identity_no:
#                 conditions.append(
#                     ((ppl_people.identity_type == req.identity_type) & (ppl_people.identity_no == req.identity_no)))
#
#             query = (
#                 client.ontology.objects.ppl_people.ppl_people_ppl_people_picture_relation.where(*conditions).order_by(
#                     ppl_people.c_time.desc()))
#             results_total = query.count_all()
#
#             offset, limit = parse_pagination_params(query_params={"page": req.page, "page_size": req.page_size})
#             raw_results = query.limit(limit).offset(offset).allObject()
#
#             return ResCode(0, "success", 200, data=raw_results, data_count=len(raw_results), count=results_total)
#         except Exception as e:
#             raise e

            # return ResCode(busiCode=HttpStatus.INTERNAL_SERVER_ERROR,
            #                busiMsg=f"系统内部错误{str(e)}",
            #                httpCode=HttpStatus.INTERNAL_SERVER_ERROR)

    # def user_detail(self, peopleCode: str):
    #     try:
    #         client = FoundryClient()
    #         user_base_info = client.ontology_new.ppl_people.where(ppl_people.sys_code == peopleCode).first()
    #         if user_base_info is None:
    #             return ResCode(busiCode=HttpStatus.INTERNAL_SERVER_ERROR,
    #                            busiMsg=f"查询用户基础信息失败",
    #                            httpCode=HttpStatus.INTERNAL_SERVER_ERROR)

            # 政治经历
            # political_experience = client.ontology_new.tymx_politician_resume.where(
            #     tymx_politician_resume.person_code == peopleCode).all()
            #
            # # 部队经历
            # military_experience = client.ontology_new.tymx_troop_resume.where(
            #     tymx_troop_resume.person_code == peopleCode).all()
            #
            # # 工作经历
            # work_experience = client.ontology_new.ppl_resume.where(ppl_resume.person_code == peopleCode).all()
            #
            # # 教育经历
            # education_experience = client.ontology_new.ppl_education.where(ppl_education.person_code == peopleCode).all()
        # except Exception as e:
        #     pass

if __name__ == '__main__':
    pass
    # req = IndexRequest(
    #     country_code="US",
    # )
    # user_list = RwUserService().get_user_list(req)
    # print(user_list)
    # print(user_list.to_dict())
    # from ontology_new.ontology_sdk.FoundryClient import FoundryClient
    # # from sthg_ontology_base_plus import FoundryClient
    # # from ontology.TGclient import TGClient
    # client = FoundryClient()
    # client_old = TGClient(["ppl_people", "ppl_people_picture"])
    # obj_b = client_old.ontology.objects.join(
    #     [ppl_people, ppl_people_picture],
    #     on_fields_list=[("id", "people_code")],
    #     join_types=["left"]
    # ).where().all()
    # print(obj_b)
    # obj_c = client.ontology.objects.join(
    #     [ppl_people, ppl_people_picture],
    #     on_fields_list=[("id", "people_code")],
    #     join_types=["left"]
    # ).where().all()
    # result = client.ontology.objects.ppl_people.where(ppl_people.id==1001).allObject()
    # for obj in result:
    #     print(obj.id)
    # print(obj_c)
