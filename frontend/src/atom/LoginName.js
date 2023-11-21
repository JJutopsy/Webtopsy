import { atom } from 'recoil';
import { recoilPersist } from 'recoil-persist';

const { persistAtom } = recoilPersist();

export const LoginName = atom({
    key: 'LoginName',
    default: "",
    effects_UNSTABLE: [persistAtom],
});