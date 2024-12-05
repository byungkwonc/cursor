# next-msw

## Next.Js MSW 적용 예

### 폴더 구조

```text
project-root/
    └── mocks/
        ├── browser.ts
        ├── handlers.ts
        ├── index.ts
        ├── server.ts
        └── api/
            ├── searchMemberResult.ts
            └── data/
                └── searchMemberResultData.ts
```

### searchMemberResultData.ts

```nextjs
export const searchMemberResultData = {
  data: {
    totalCount: 2903,
    size: 10,
    offset: 0,
    orders: [],
    page: 1,
    hasNext: true,
    pageRows: [
      {
        memberSeq: 3245,
        memberNick: '요가하는비버4347',
        memberType: 'M',
      },
      {
        memberSeq: 3244,
        memberNick: '피구하는문어8612',
        memberType: 'M',
      },
      {
        memberSeq: 3243,
        memberNick: '댄싱머신불곰9486',
        memberType: 'M',
      },
      {
        memberSeq: 3242,
        memberNick: '수영하는낙타9739',
        memberType: 'M',
      },
      {
        memberSeq: 3241,
        memberNick: '펜싱하는참새9817',
        memberType: 'M',
      },
    ],
  },
};
```

### searchMemberResult.ts

```nextjs
import { searchMemberResultData } from 'mocks/api/data/searchMemberResultData';
import { rest } from 'msw';

// 첫 번째 인자로 경로, 두 번째 인자로 request, response, context를 파라미터로 넘겨받는 콜백 함수를 넣어준다.
// 원하는 API가 여러 개라면 handlers 배열에 여러 개를 넣어주면 된다.

const handlers = [
  // 회원 조회
  rest.get('/members', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(searchMemberResultData));
  }),
];

export default handlers;
```

### handler

```nextjs
// handlers.ts

import searchResultHandler from './api/searchMemberResult';

export const handlers = [...searchResultHandler];

// browser.ts
// 브라우저 환경설정

import { setupWorker } from 'msw';
import { handlers } from './handlers';

export const worker = setupWorker(...handlers);

// server.ts
// node 환경설정

import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

### index.ts

```nextjs
async function initMocks() {
  if (typeof window === 'undefined') {
    const { server } = await import('./server');
    server.listen();
  } else {
    const { worker } = await import('./browser');
    worker.start();
  }
}

initMocks();

export {};
```

### _app.tsx

```
if (process.env.NODE_ENV === 'development') {
  import('../mocks');
}
```

### 사용

```react
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { MEMBER } from 'constants/@queryKeys';

const SearchMember = () => {
  const getMembers = async () => {
    const { data } = await axios.get('/members');
    return data;
  };

  const { data: memberList } = useQuery([MEMBER.LIST], getMembers);

  console.log(memberList);

  return <div>회원 검색</div>;
};

export default SearchMember;
```
