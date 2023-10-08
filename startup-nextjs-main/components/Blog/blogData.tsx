import { Blog } from "@/types/blog";

const blogData: Blog[] = [
  {
    id: 1,
    title: "Ali Aslanbayli",
    paragraph:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sit amet dictum neque, laoreet dolor.",
    image: "/images/blog/blog-01.jpg",
    author: {
      name: "Ali's resume",
      image: "/images/blog/author-01.png",
      designation: "Full-stack developer",
    },
    tags: [""],
    publishDate: "Class of 2024" ,
  },
  {
    id: 2,
    title: "Fariz Zeynalov",
    paragraph:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sit amet dictum neque, laoreet dolor.",
    image: "/images/blog/blog-02.jpg",
    author: {
      name: "Fariz's resume",
      image: "/images/blog/author-02.png",
      designation: "Full-stack developer",
    },
    tags: ["computer"],
    publishDate: "Class of 2026",
  },
  {
    id: 3,
    title: "Chloe Berry",
    paragraph:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sit amet dictum neque, laoreet dolor.",
    image: "/images/blog/blog-03.jpg",
    author: {
      name: "Chloe's resume",
      image: "/images/blog/author-03.png",
      designation: "Full-stack developer",
    },
    tags: ["design"],
    publishDate: "Class of 2024",
  },
  {
    id: 4,
    title: "Aleksandre Papunashvili",
    paragraph:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sit amet dictum neque, laoreet dolor.",
    image: "/images/blog/blog-03.jpg",
    author: {
      name: "Aleksandre's resume",
      image: "/images/blog/author-03.png",
      designation: "Full-stack developer",
    },
    tags: ["design"],
    publishDate: "Class of 2026",
  },
];
export default blogData;
