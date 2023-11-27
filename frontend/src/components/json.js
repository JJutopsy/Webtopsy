export const json = {
  title: "기초 환자 정보",
  description: "Description of AMSout1",
  logoPosition: "right",
  pages: [
    {
      name: "page1",
      elements: [
        {
          type: "text",
          name: "VisitCount",
          title: "병원 방문 횟수",
          inputType: "number",
        },
        {
          type: "multipletext",
          name: "BasicInfo",
          title: "환자 건강 정보",
          items: [
            {
              name: "height",
              inputType: "number",
              title: "키",
            },
            {
              name: "weight",
              inputType: "number",
              title: "몸무게",
            },
            {
              name: "HbA1c",
              inputType: "number",
              title: "혈당",
            },
          ],
        },
        {
          type: "text",
          name: "lastdate",
          title: "마지막 방문 날짜",
          inputType: "datetime-local",
        },
      ],
    },
  ],
};
