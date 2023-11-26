import { atom } from 'recoil';

// 버튼 상태를 나타내는 atom 생성
export const buttonState = atom({
  key: 'buttonState',
  default: false, // 기본값은 false로 설정
});
