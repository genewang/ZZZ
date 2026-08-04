import { PromoBar, Nav } from "./components/Nav";
import { Hero } from "./components/Hero";
import { HowItWorks } from "./components/HowItWorks";
import { Kits } from "./components/Kits";
import { CreateStudio } from "./components/CreateStudio";
import { InsideBox } from "./components/InsideBox";
import { Trust } from "./components/Trust";
import { SystemDiagrams } from "./components/SystemDiagrams";
import { Stories } from "./components/Stories";
import { Churches } from "./components/Churches";
import { Faq } from "./components/Faq";
import { Closing } from "./components/Closing";
import { SiteFooter } from "./components/SiteFooter";
import "./App.css";

export default function App() {
  return (
    <>
      <PromoBar />
      <Nav />
      <main>
        <Hero />
        <HowItWorks />
        <Kits />
        <CreateStudio />
        <InsideBox />
        <Trust />
        <SystemDiagrams />
        <Stories />
        <Churches />
        <Faq />
        <Closing />
      </main>
      <SiteFooter />
    </>
  );
}
