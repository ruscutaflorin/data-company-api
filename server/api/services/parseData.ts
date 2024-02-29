import fs from "fs";
import * as csv from "fast-csv";
import { CompanyProfile } from "../types/data";

const parseDataFromFile = (path: string): Promise<CompanyProfile[]> => {
  return new Promise((resolve, reject) => {
    const results: CompanyProfile[] = [];

    fs.createReadStream(path)
      .pipe(csv.parse({ headers: true }))
      .on("data", (row: CompanyProfile) => {
        results.push(row);
      })
      .on("end", () => {
        console.log("CSV file successfully parsed");
        resolve(results);
      })
      .on("error", (error) => {
        console.error("Error parsing CSV file:", error);
        reject(error);
      });
  });
};

export const receivedData = parseDataFromFile("../API-input-sample.csv")
  .then((companyProfiles) => {
    console.log("Parsed company profiles:", companyProfiles);
  })
  .catch((error) => {
    console.error("Error parsing data:", error);
  });
