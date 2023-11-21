import React, { useEffect, useState } from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Header from '../components/Header';
import StickyFooter from '../components/StickyFooter';
import { useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown'


const ProblemView = () => {
    const { no } = useParams();
    const markdown =
        `### 상근이의 상근날드
    상근이는 세계 최대 규모의 햄버거 가게 상근날드의 직원입니다. 상근날드의 가장 유명한 메뉴는 Priority_Queue 버거 입니다. Proiorty_Queue버거는 햄버거의 구성 요소 중
    우선순위가 높은 재료부터 먼저 먹을 수 있게 만든 구조의 햄버거 입니다. 상근이는 상근날드의 명예 크루원이기 때문에 리그오브레전드를 좋아합니다.

![5](https://user-images.githubusercontent.com/43310141/215344146-d575f689-67a0-4e9c-bf17-de51dad3347c.gif)

<상근이의 롤 실력 중 발췌>

참고로 상근이가 트린다미어였다! 아무튼 상근이는 리그오브레전드도 좋아하지만 햄버거 일도 미룰 순 없습니다. 그래서 리그오브레전드와 상근날드의 비율이 각각 전체 시간의 50%가 되도록 노력하려 합니다. 상근이는 상남자이기 때문에 하루에 리그오브레전드를 하거나 상근날드에 출근하거나 둘 중 하나를 선택합니다. 만약 오늘은 리그오브레전드를 하기로 결정하면, 출근하지 않습니다.

그리고 상근이가 하루에 리그오브레전드를 하거나 상근날드에서 일 할 때는 T 만큼의 시간이 소요된다고 할 때,

상근이를 도와 리그오브레전드를 할 때 드는 노력 수치 L과 상근날드의 노력 수치 S 가 주어질 때 리그오브레전드의 노력 수치와 상근날드의 노력 수치가 정확히 같게 되는 날이 언제인지 출력 해주세요.

만약 같게 만드는 경우가 없을 경우 -1을 출력합니다.

    `;
    return (
        <>
            <Container component="main" sx={{ mt: 5 }} maxWidth="lg">
                <h1> {no}번 문제</h1>
                <ReactMarkdown children={markdown} />
            </Container>
            <StickyFooter />
        </>
    );
};
export default ProblemView;