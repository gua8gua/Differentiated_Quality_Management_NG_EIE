interface CoreWorksProps {
  works: string[];
}

const descriptions = [
  "完成质量数据清洗、异常识别、标准化和综合评价。",
  "构建质控知识图谱，实现质量问题根因追溯。",
  "展示潜在风险预测和三类智能体协同处置闭环。",
];

export function CoreWorks({ works }: CoreWorksProps) {
  return (
    <section className="grid three">
      {works.map((work, index) => (
        <article className="card" key={work}>
          <span className="index">0{index + 1}</span>
          <h2>{work}</h2>
          <p>{descriptions[index]}</p>
        </article>
      ))}
    </section>
  );
}

